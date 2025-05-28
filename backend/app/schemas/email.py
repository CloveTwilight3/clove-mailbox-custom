from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


class EmailAddress(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class EmailAttachment(BaseModel):
    filename: str
    content_type: str
    size: int
    content_id: Optional[str] = None


class EmailBase(BaseModel):
    subject: Optional[str] = None
    sender_email: EmailStr
    sender_name: Optional[str] = None
    reply_to: Optional[str] = None
    
    to_addresses: Optional[List[Dict[str, str]]] = None
    cc_addresses: Optional[List[Dict[str, str]]] = None
    bcc_addresses: Optional[List[Dict[str, str]]] = None
    
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    
    folder: str = "INBOX"
    labels: Optional[List[str]] = None


class EmailCreate(EmailBase):
    account_id: int
    message_id: str
    uid: Optional[str] = None
    date_sent: Optional[datetime] = None
    date_received: Optional[datetime] = None
    size: Optional[int] = None


class EmailUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_starred: Optional[bool] = None
    is_deleted: Optional[bool] = None
    folder: Optional[str] = None
    labels: Optional[List[str]] = None


class EmailInDB(EmailBase):
    id: int
    account_id: int
    message_id: str
    uid: Optional[str] = None
    thread_id: Optional[str] = None
    
    date_sent: Optional[datetime] = None
    date_received: Optional[datetime] = None
    size: Optional[int] = None
    
    is_read: bool
    is_starred: bool
    is_deleted: bool
    is_draft: bool
    is_sent: bool
    
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Email(EmailInDB):
    pass


class EmailCompose(BaseModel):
    account_id: int
    to_addresses: List[EmailAddress]
    cc_addresses: Optional[List[EmailAddress]] = None
    bcc_addresses: Optional[List[EmailAddress]] = None
    subject: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    attachments: Optional[List[str]] = None  # File paths or IDs


class EmailReply(BaseModel):
    original_email_id: int
    account_id: int
    to_addresses: List[EmailAddress]
    cc_addresses: Optional[List[EmailAddress]] = None
    subject: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    reply_all: bool = False


class EmailForward(BaseModel):
    original_email_id: int
    account_id: int
    to_addresses: List[EmailAddress]
    cc_addresses: Optional[List[EmailAddress]] = None
    subject: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None


class EmailSearch(BaseModel):
    query: str
    folder: Optional[str] = None
    sender: Optional[str] = None
    subject: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    is_read: Optional[bool] = None
    is_starred: Optional[bool] = None
    has_attachments: Optional[bool] = None
