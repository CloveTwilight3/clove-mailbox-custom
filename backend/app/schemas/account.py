from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class EmailAccountBase(BaseModel):
    name: str
    email_address: EmailStr
    display_name: Optional[str] = None
    
    # IMAP Configuration
    imap_host: str
    imap_port: int
    imap_ssl: bool = True
    imap_username: str
    
    # SMTP Configuration
    smtp_host: str
    smtp_port: int
    smtp_ssl: bool = True
    smtp_username: str
    
    # POP3 Configuration (optional)
    pop3_host: Optional[str] = None
    pop3_port: Optional[int] = None
    pop3_ssl: bool = True
    pop3_username: Optional[str] = None


class EmailAccountCreate(EmailAccountBase):
    imap_password: str
    smtp_password: str
    pop3_password: Optional[str] = None


class EmailAccountUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    imap_password: Optional[str] = None
    smtp_password: Optional[str] = None
    pop3_password: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class EmailAccountInDB(EmailAccountBase):
    id: int
    user_id: int
    avatar_url: Optional[str] = None
    is_active: bool
    is_default: bool
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmailAccount(EmailAccountInDB):
    # Public version without sensitive data
    pass


class EmailAccountWithStatus(EmailAccount):
    connection_status: dict = {}  # Contains connection test results


class AccountConnectionTest(BaseModel):
    imap_success: bool
    smtp_success: bool
    pop3_success: Optional[bool] = None
    error_message: Optional[str] = None
