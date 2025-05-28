import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Tuple
import logging
import os

from app.schemas.email import EmailCompose, EmailAddress
from app.schemas.account import EmailAccount

logger = logging.getLogger(__name__)


class SMTPService:
    def __init__(self, account: EmailAccount, password: str):
        self.account = account
        self.password = password
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to SMTP server"""
        try:
            if self.account.smtp_ssl:
                self.connection = smtplib.SMTP_SSL(
                    self.account.smtp_host,
                    self.account.smtp_port
                )
            else:
                self.connection = smtplib.SMTP(
                    self.account.smtp_host,
                    self.account.smtp_port
                )
                self.connection.starttls()
            
            self.connection.login(self.account.smtp_username, self.password)
            logger.info(f"Successfully connected to SMTP server for {self.account.email_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from SMTP server"""
        if self.connection:
            try:
                self.connection.quit()
            except:
                pass
            self.connection = None
    
    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """Test SMTP connection"""
        try:
            if self.connect():
                self.disconnect()
                return True, None
            return False, "Failed to connect"
        except Exception as e:
            return False, str(e)
    
    def send_email(self, email_data: EmailCompose) -> Tuple[bool, Optional[str]]:
        """Send an email"""
        if not self.connection:
            if not self.connect():
                return False, "Could not connect to SMTP server"
        
        try:
            msg = self._create_message(email_data)
            
            # Get recipient emails
            to_emails = [addr.email for addr in email_data.to_addresses]
            cc_emails = [addr.email for addr in email_data.cc_addresses] if email_data.cc_addresses else []
            bcc_emails = [addr.email for addr in email_data.bcc_addresses] if email_data.bcc_addresses else []
            
            all_recipients = to_emails + cc_emails + bcc_emails
            
            # Send the email
            self.connection.send_message(msg, to_addrs=all_recipients)
            
            logger.info(f"Email sent successfully from {self.account.email_address}")
            return True, None
            
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _create_message(self, email_data: EmailCompose) -> MIMEMultipart:
        """Create email message"""
        msg = MIMEMultipart('alternative')
        
        # Set headers
        msg['From'] = f"{self.account.display_name} <{self.account.email_address}>" if self.account.display_name else self.account.email_address
        msg['To'] = ', '.join([f"{addr.name} <{addr.email}>" if addr.name else addr.email for addr in email_data.to_addresses])
        
        if email_data.cc_addresses:
            msg['Cc'] = ', '.join([f"{addr.name} <{addr.email}>" if addr.name else addr.email for addr in email_data.cc_addresses])
        
        msg['Subject'] = email_data.subject
        
        # Add body content
        if email_data.body_text:
            text_part = MIMEText(email_data.body_text, 'plain', 'utf-8')
            msg.attach(text_part)
        
        if email_data.body_html:
            html_part = MIMEText(email_data.body_html, 'html', 'utf-8')
            msg.attach(html_part)
        
        # Add attachments
        if email_data.attachments:
            for attachment_path in email_data.attachments:
                self._add_attachment(msg, attachment_path)
        
        return msg
    
    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """Add file attachment to email"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Attachment file not found: {file_path}")
                return
            
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            
            filename = os.path.basename(file_path)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            msg.attach(part)
            
        except Exception as e:
            logger.error(f"Error adding attachment {file_path}: {str(e)}")
    
    def send_reply(self, original_message_id: str, email_data: EmailCompose) -> Tuple[bool, Optional[str]]:
        """Send a reply to an existing email"""
        # Modify subject to include "Re:" prefix
        if not email_data.subject.startswith("Re:"):
            email_data.subject = f"Re: {email_data.subject}"
        
        # Set In-Reply-To header for threading
        if not self.connection:
            if not self.connect():
                return False, "Could not connect to SMTP server"
        
        try:
            msg = self._create_message(email_data)
            msg['In-Reply-To'] = original_message_id
            msg['References'] = original_message_id
            
            # Get recipient emails
            to_emails = [addr.email for addr in email_data.to_addresses]
            cc_emails = [addr.email for addr in email_data.cc_addresses] if email_data.cc_addresses else []
            bcc_emails = [addr.email for addr in email_data.bcc_addresses] if email_data.bcc_addresses else []
            
            all_recipients = to_emails + cc_emails + bcc_emails
            
            # Send the email
            self.connection.send_message(msg, to_addrs=all_recipients)
            
            logger.info(f"Reply sent successfully from {self.account.email_address}")
            return True, None
            
        except Exception as e:
            error_msg = f"Failed to send reply: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def send_forward(self, email_data: EmailCompose) -> Tuple[bool, Optional[str]]:
        """Send a forwarded email"""
        # Modify subject to include "Fwd:" prefix
        if not email_data.subject.startswith("Fwd:"):
            email_data.subject = f"Fwd: {email_data.subject}"
        
        return self.send_email(email_data)
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
