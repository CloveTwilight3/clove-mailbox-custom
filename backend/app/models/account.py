from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class EmailAccount(Base):
    __tablename__ = "email_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Account Information
    name = Column(String, nullable=False)  # Display name for the account
    email_address = Column(String, nullable=False)
    display_name = Column(String, nullable=True)  # User's display name for emails
    avatar_url = Column(String, nullable=True)  # Profile image URL
    
    # IMAP Configuration
    imap_host = Column(String, nullable=False)
    imap_port = Column(Integer, nullable=False)
    imap_ssl = Column(Boolean, default=True)
    imap_username = Column(String, nullable=False)
    imap_password = Column(Text, nullable=False)  # Encrypted
    
    # SMTP Configuration
    smtp_host = Column(String, nullable=False)
    smtp_port = Column(Integer, nullable=False)
    smtp_ssl = Column(Boolean, default=True)
    smtp_username = Column(String, nullable=False)
    smtp_password = Column(Text, nullable=False)  # Encrypted
    
    # POP3 Configuration (optional)
    pop3_host = Column(String, nullable=True)
    pop3_port = Column(Integer, nullable=True)
    pop3_ssl = Column(Boolean, default=True)
    pop3_username = Column(String, nullable=True)
    pop3_password = Column(Text, nullable=True)  # Encrypted
    
    # Account Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="accounts")
    emails = relationship("Email", back_populates="account")
