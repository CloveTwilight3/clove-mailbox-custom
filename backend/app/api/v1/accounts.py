from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from PIL import Image

from app.core.database import get_db
from app.core.config import settings
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.account import EmailAccount
from app.schemas.account import (
    EmailAccount as EmailAccountSchema,
    EmailAccountCreate,
    EmailAccountUpdate,
    EmailAccountWithStatus,
    AccountConnectionTest
)
from app.services.imap_service import IMAPService
from app.services.smtp_service import SMTPService

router = APIRouter()


@router.get("/", response_model=List[EmailAccountSchema])
async def get_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all email accounts for the current user"""
    accounts = db.query(EmailAccount).filter(EmailAccount.user_id == current_user.id).all()
    return accounts


@router.post("/", response_model=EmailAccountSchema)
async def create_account(
    account_data: EmailAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new email account"""
    
    # Check if email account already exists for this user
    existing = db.query(EmailAccount).filter(
        EmailAccount.user_id == current_user.id,
        EmailAccount.email_address == account_data.email_address
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email account already exists"
        )
    
    # TODO: Encrypt passwords before storing
    # For now, we'll store them as-is (NOT SECURE - implement encryption)
    
    # Create new account
    db_account = EmailAccount(
        user_id=current_user.id,
        name=account_data.name,
        email_address=account_data.email_address,
        display_name=account_data.display_name,
        imap_host=account_data.imap_host,
        imap_port=account_data.imap_port,
        imap_ssl=account_data.imap_ssl,
        imap_username=account_data.imap_username,
        imap_password=account_data.imap_password,  # TODO: Encrypt
        smtp_host=account_data.smtp_host,
        smtp_port=account_data.smtp_port,
        smtp_ssl=account_data.smtp_ssl,
        smtp_username=account_data.smtp_username,
        smtp_password=account_data.smtp_password,  # TODO: Encrypt
        pop3_host=account_data.pop3_host,
        pop3_port=account_data.pop3_port,
        pop3_ssl=account_data.pop3_ssl,
        pop3_username=account_data.pop3_username,
        pop3_password=account_data.pop3_password,  # TODO: Encrypt
    )
    
    # If this is the first account, make it default
    user_accounts_count = db.query(EmailAccount).filter(EmailAccount.user_id == current_user.id).count()
    if user_accounts_count == 0:
        db_account.is_default = True
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return db_account


@router.get("/{account_id}", response_model=EmailAccountSchema)
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific email account"""
    account = db.query(EmailAccount).filter(
        EmailAccount.id == account_id,
        EmailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    return account


@router.put("/{account_id}", response_model=EmailAccountSchema)
async def update_account(
    account_id: int,
    account_update: EmailAccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an email account"""
    account = db.query(EmailAccount).filter(
        EmailAccount.id == account_id,
        EmailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    # Update fields
    update_data = account_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field.endswith('_password') and value:
            # TODO: Encrypt password
            setattr(account, field, value)
        else:
            setattr(account, field, value)
    
    # If setting as default, unset other defaults
    if account_update.is_default:
        db.query(EmailAccount).filter(
            EmailAccount.user_id == current_user.id,
            EmailAccount.id != account_id
        ).update({"is_default": False})
    
    db.commit()
    db.refresh(account)
    
    return account


@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an email account"""
    account = db.query(EmailAccount).filter(
        EmailAccount.id == account_id,
        EmailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    db.delete(account)
    db.commit()
    
    return {"message": "Email account deleted successfully"}


@router.post("/{account_id}/test", response_model=AccountConnectionTest)
async def test_account_connection(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test email account connection"""
    account = db.query(EmailAccount).filter(
        EmailAccount.id == account_id,
        EmailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    # TODO: Decrypt passwords
    imap_password = account.imap_password
    smtp_password = account.smtp_password
    
    test_result = AccountConnectionTest(
        imap_success=False,
        smtp_success=False,
        pop3_success=None
    )
    
    try:
        # Test IMAP connection
        imap_service = IMAPService(account, imap_password)
        imap_success, imap_error = imap_service.test_connection()
        test_result.imap_success = imap_success
        
        # Test SMTP connection
        smtp_service = SMTPService(account, smtp_password)
        smtp_success, smtp_error = smtp_service.test_connection()
        test_result.smtp_success = smtp_success
        
        # Set error message if any test failed
        if not imap_success or not smtp_success:
            errors = []
            if not imap_success and imap_error:
                errors.append(f"IMAP: {imap_error}")
            if not smtp_success and smtp_error:
                errors.append(f"SMTP: {smtp_error}")
            test_result.error_message = "; ".join(errors)
        
    except Exception as e:
        test_result.error_message = str(e)
    
    return test_result


@router.post("/{account_id}/avatar")
async def upload_avatar(
    account_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile avatar for email account"""
    account = db.query(EmailAccount).filter(
        EmailAccount.id == account_id,
        EmailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Check file size
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size must be less than {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension"
        )
    
    filename = f"avatar_{account_id}_{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    try:
        # Save and resize image
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Resize image to 200x200
        with Image.open(file_path) as img:
            img = img.resize((200, 200), Image.Resampling.LANCZOS)
            img.save(file_path, optimize=True, quality=85)
        
        # Update account with avatar URL
        avatar_url = f"/uploads/{filename}"
        account.avatar_url = avatar_url
        db.commit()
        
        return {"avatar_url": avatar_url, "message": "Avatar uploaded successfully"}
        
    except Exception as e:
        # Clean up file if something went wrong
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )


@router.get("/{account_id}/folders")
async def get_folders(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available folders for an email account"""
    account = db.query(EmailAccount).filter(
        EmailAccount.id == account_id,
        EmailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email account not found"
        )
    
    # TODO: Decrypt password
    password = account.imap_password
    
    try:
        with IMAPService(account, password) as imap:
            folders = imap.get_folders()
            return {"folders": folders}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting folders: {str(e)}"
        )
