from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.email import Email
from app.models.account import EmailAccount
from app.schemas.email import (
    Email as EmailSchema, 
    EmailCreate, 
    EmailUpdate, 
    EmailCompose,
    EmailSearch
)
from app.services.imap_service import IMAPService
from app.services.smtp_service import SMTPService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[EmailSchema])
async def get_emails(
    account_id: Optional[int] = Query(None),
    folder: str = Query("INBOX"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get emails for the current user"""
    
    # Build query
    query = db.query(Email).join(EmailAccount).filter(EmailAccount.user_id == current_user.id)
    
    if account_id:
        query = query.filter(Email.account_id == account_id)
    
    if folder:
        query = query.filter(Email.folder == folder)
    
    # Order by date received (most recent first)
    query = query.order_by(Email.date_received.desc())
    
    # Apply pagination
    emails = query.offset(offset).limit(limit).all()
    
    return emails


@router.get("/{email_id}", response_model=EmailSchema)
async def get_email(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific email by ID"""
    
    email = db.query(Email).join(EmailAccount).filter(
        Email.id == email_id,
        EmailAccount.user_id == current_user.id
    ).first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # If we don't have body content, try to fetch it from IMAP
    if not email.body_text and not email.body_html and email.uid:
        try:
            account = email.account
            password = account.imap_password  # TODO: Decrypt password
            
            imap_service = IMAPService(account, password)
            if imap_service.connect():
                try:
                    email_content = imap_service.get_email_content(email.uid)
                    if email_content:
                        # Update the email record with full content
                        email.body_text = email_content.get('body_text')
                        email.body_html = email_content.get('body_html')
                        email.attachments = email_content.get('attachments')
                        db.commit()
                        logger.info(f"Updated email {email_id} with full content")
                finally:
                    imap_service.disconnect()
        except Exception as e:
            logger.warning(f"Could not fetch full email content for email {email_id}: {str(e)}")
    
    return email


@router.put("/{email_id}", response_model=EmailSchema)
async def update_email(
    email_id: int,
    email_update: EmailUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update email (mark as read/unread, star, etc.)"""
    
    email = db.query(Email).join(EmailAccount).filter(
        Email.id == email_id,
        EmailAccount.user_id == current_user.id
    ).first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Update fields
    for field, value in email_update.dict(exclude_unset=True).items():
        setattr(email, field, value)
    
    db.commit()
    db.refresh(email)
    
    return email


@router.delete("/{email_id}")
async def delete_email(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an email"""
    
    email = db.query(Email).join(EmailAccount).filter(
        Email.id == email_id,
        EmailAccount.user_id == current_user.id
    ).first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Mark as deleted instead of actually deleting
    email.is_deleted = True
    db.commit()
    
    return {"message": "Email deleted successfully"}


@router.post("/compose")
async def compose_email(
    email_data: EmailCompose,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compose and send a new email"""
    
    # Get the email account
    account = db.query(EmailAccount).filter(
        EmailAccount.id == email_data.account_id,
        EmailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    # TODO: Implement proper password decryption
    # For now, use stored password directly (NOT SECURE)
    password = account.smtp_password
    
    try:
        # Send email via SMTP
        with SMTPService(account, password) as smtp:
            success, error = smtp.send_email(email_data)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to send email: {error}"
                )
        
        return {"message": "Email sent successfully"}
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending email: {str(e)}"
        )


@router.post("/sync/{account_id}")
async def sync_emails(
    account_id: int,
    folder: str = Query("INBOX"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync emails from IMAP server"""
    
    # Get the email account
    account = db.query(EmailAccount).filter(
        EmailAccount.id == account_id,
        EmailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    # TODO: Implement proper password decryption
    # For now, use stored password directly (NOT SECURE)
    password = account.imap_password
    
    try:
        # Fetch emails via IMAP
        imap_service = IMAPService(account, password)
        
        if not imap_service.connect():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not connect to IMAP server"
            )
        
        try:
            logger.info(f"Starting email sync for account {account_id}, folder {folder}")
            email_list = imap_service.get_email_list(folder=folder, limit=50)
            logger.info(f"Retrieved {len(email_list)} emails from IMAP server")
            
            synced_count = 0
            updated_count = 0
            
            for email_data in email_list:
                try:
                    # Check if email already exists
                    existing = db.query(Email).filter(
                        Email.message_id == email_data.get('message_id', ''),
                        Email.account_id == account_id
                    ).first()
                    
                    if not existing:
                        # For new emails, try to get full content if UID is available
                        full_content = None
                        if email_data.get('uid'):
                            try:
                                full_content = imap_service.get_email_content(email_data['uid'])
                            except Exception as e:
                                logger.debug(f"Could not fetch full content for UID {email_data.get('uid')}: {e}")
                        
                        # Use full content if available, otherwise use header data
                        content_data = full_content if full_content else email_data
                        
                        # Create new email record
                        new_email = Email(
                            account_id=account_id,
                            message_id=content_data.get('message_id', ''),
                            uid=content_data.get('uid'),
                            subject=content_data.get('subject'),
                            sender_email=content_data.get('sender_email', ''),
                            sender_name=content_data.get('sender_name'),
                            reply_to=content_data.get('reply_to'),
                            to_addresses=content_data.get('to_addresses'),
                            body_text=content_data.get('body_text'),
                            body_html=content_data.get('body_html'),
                            attachments=content_data.get('attachments'),
                            date_sent=content_data.get('date_sent'),
                            date_received=content_data.get('date_received'),
                            size=content_data.get('size', 0),
                            is_read=content_data.get('is_read', False),
                            folder=folder
                        )
                        
                        db.add(new_email)
                        synced_count += 1
                    else:
                        # Update existing email if read status changed
                        if existing.is_read != email_data.get('is_read', False):
                            existing.is_read = email_data.get('is_read', False)
                            updated_count += 1
                            
                except Exception as e:
                    logger.error(f"Error processing email {email_data.get('uid', 'unknown')}: {str(e)}")
                    continue
            
            # Update account last sync time
            from datetime import datetime
            account.last_sync = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Sync completed: {synced_count} new emails, {updated_count} updated emails")
            
        finally:
            imap_service.disconnect()
            
        message = f"Successfully synced {synced_count} new emails"
        if updated_count > 0:
            message += f" and updated {updated_count} existing emails"
            
        return {"message": message}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error syncing emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing emails: {str(e)}"
        )


@router.post("/search", response_model=List[EmailSchema])
async def search_emails(
    search_data: EmailSearch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search emails"""
    
    query = db.query(Email).join(EmailAccount).filter(EmailAccount.user_id == current_user.id)
    
    # Apply search filters
    if search_data.query:
        query = query.filter(
            Email.subject.contains(search_data.query) |
            Email.body_text.contains(search_data.query) |
            Email.sender_email.contains(search_data.query)
        )
    
    if search_data.folder:
        query = query.filter(Email.folder == search_data.folder)
    
    if search_data.sender:
        query = query.filter(Email.sender_email.contains(search_data.sender))
    
    if search_data.subject:
        query = query.filter(Email.subject.contains(search_data.subject))
    
    if search_data.date_from:
        query = query.filter(Email.date_received >= search_data.date_from)
    
    if search_data.date_to:
        query = query.filter(Email.date_received <= search_data.date_to)
    
    if search_data.is_read is not None:
        query = query.filter(Email.is_read == search_data.is_read)
    
    if search_data.is_starred is not None:
        query = query.filter(Email.is_starred == search_data.is_starred)
    
    emails = query.order_by(Email.date_received.desc()).limit(100).all()
    
    return emails
