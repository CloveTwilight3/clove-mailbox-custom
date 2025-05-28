from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("email_accounts.id"), nullable=False)
    
    # Email Identifiers
    message_id = Column(String, nullable=False, index=True)  # Unique message ID
    uid = Column(String, nullable=True, index=True)  # IMAP UID
    thread_id = Column(String, nullable=True, index=True)  # For threading
    
    # Email Headers
    subject = Column(String, nullable=True)
    sender_name = Column(String, nullable=True)
    sender_email = Column(String, nullable=False, index=True)
    reply_to = Column(String, nullable=True)
    
    # Recipients
    to_addresses = Column(JSON, nullable=True)  # List of recipients
    cc_addresses = Column(JSON, nullable=True)  # CC recipients
    bcc_addresses = Column(JSON, nullable=True)  # BCC recipients
    
    # Email Content
    body_text = Column(Text, nullable=True)  # Plain text body
    body_html = Column(Text, nullable=True)  # HTML body
    attachments = Column(JSON, nullable=True)  # List of attachment info
    
    # Email Metadata
    date_sent = Column(DateTime(timezone=True), nullable=True)
    date_received = Column(DateTime(timezone=True), nullable=True)
    size = Column(Integer, nullable=True)  # Size in bytes
    
    # Email Status
    is_read = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    is_draft = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    
    # Folder/Label Information
    folder = Column(String, default="INBOX")  # IMAP folder
    labels = Column(JSON, nullable=True)  # List of labels/tags
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    account = relationship("EmailAccount", back_populates="emails")
