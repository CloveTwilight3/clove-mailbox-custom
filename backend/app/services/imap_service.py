import imaplib
import email
import email.utils
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

from app.schemas.email import EmailCreate
from app.schemas.account import EmailAccount

logger = logging.getLogger(__name__)


class IMAPService:
    def __init__(self, account: EmailAccount, password: str):
        self.account = account
        self.password = password
        self.connection = None
        
    def connect(self) -> bool:
        """Connect to IMAP server"""
        try:
            if self.account.imap_ssl:
                self.connection = imaplib.IMAP4_SSL(
                    self.account.imap_host, 
                    self.account.imap_port
                )
            else:
                self.connection = imaplib.IMAP4(
                    self.account.imap_host, 
                    self.account.imap_port
                )
            
            self.connection.login(self.account.imap_username, self.password)
            logger.info(f"Successfully connected to IMAP server for {self.account.email_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from IMAP server"""
        if self.connection:
            try:
                self.connection.logout()
            except:
                pass
            self.connection = None
    
    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """Test IMAP connection"""
        try:
            if self.connect():
                self.disconnect()
                return True, None
            return False, "Failed to connect"
        except Exception as e:
            return False, str(e)
    
    def get_folders(self) -> List[str]:
        """Get list of available folders"""
        if not self.connection:
            self.connect()
            
        try:
            status, folders = self.connection.list()
            folder_list = []
            
            if status == 'OK':
                for folder in folders:
                    # Parse folder name from IMAP response
                    folder_name = folder.decode().split('"')[-2]
                    folder_list.append(folder_name)
                    
            return folder_list
        except Exception as e:
            logger.error(f"Error getting folders: {str(e)}")
            return ["INBOX"]
    
    def select_folder(self, folder: str = "INBOX") -> bool:
        """Select a folder"""
        if not self.connection:
            self.connect()
            
        try:
            status, messages = self.connection.select(folder)
            return status == 'OK'
        except Exception as e:
            logger.error(f"Error selecting folder {folder}: {str(e)}")
            return False
    
    def get_email_list(self, folder: str = "INBOX", limit: int = 50) -> List[Dict]:
        """Get list of emails from folder"""
        if not self.select_folder(folder):
            return []
            
        try:
            # Search for all emails
            status, messages = self.connection.search(None, 'ALL')
            
            if status != 'OK':
                return []
            
            email_ids = messages[0].split()
            email_list = []
            
            # Get the most recent emails (reverse order)
            recent_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            recent_ids.reverse()
            
            for email_id in recent_ids:
                email_data = self._fetch_email_headers(email_id)
                if email_data:
                    email_list.append(email_data)
            
            return email_list
            
        except Exception as e:
            logger.error(f"Error getting email list: {str(e)}")
            return []
    
    def get_email_content(self, uid: str) -> Optional[Dict]:
        """Get full email content by UID"""
        if not self.connection:
            self.connect()
            
        try:
            status, msg_data = self.connection.fetch(uid, '(RFC822)')
            
            if status != 'OK':
                return None
                
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            return self._parse_email_message(email_message, uid)
            
        except Exception as e:
            logger.error(f"Error getting email content: {str(e)}")
            return None
    
    def mark_as_read(self, uid: str) -> bool:
        """Mark email as read"""
        if not self.connection:
            self.connect()
            
        try:
            self.connection.store(uid, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"Error marking email as read: {str(e)}")
            return False
    
    def mark_as_unread(self, uid: str) -> bool:
        """Mark email as unread"""
        if not self.connection:
            self.connect()
            
        try:
            self.connection.store(uid, '-FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"Error marking email as unread: {str(e)}")
            return False
    
    def delete_email(self, uid: str) -> bool:
        """Delete email"""
        if not self.connection:
            self.connect()
            
        try:
            self.connection.store(uid, '+FLAGS', '\\Deleted')
            self.connection.expunge()
            return True
        except Exception as e:
            logger.error(f"Error deleting email: {str(e)}")
            return False
    
    def _fetch_email_headers(self, email_id: bytes) -> Optional[Dict]:
        """Fetch email headers for list display"""
        try:
            status, msg_data = self.connection.fetch(email_id, '(ENVELOPE FLAGS)')
            
            if status != 'OK':
                return None
            
            # Parse the response
            envelope_data = msg_data[0][1]
            flags_data = msg_data[0][0]
            
            # This is a simplified parser - in production you'd want more robust parsing
            return {
                'uid': email_id.decode(),
                'subject': 'Email Subject',  # Simplified - would parse from envelope
                'sender': 'sender@example.com',  # Simplified
                'date': datetime.now(),  # Simplified
                'is_read': b'\\Seen' in flags_data,
                'size': 0  # Would be calculated
            }
            
        except Exception as e:
            logger.error(f"Error fetching email headers: {str(e)}")
            return None
    
    def _parse_email_message(self, msg: email.message.Message, uid: str) -> Dict:
        """Parse email message into structured data"""
        try:
            # Extract basic info
            subject = msg.get('Subject', '')
            sender = msg.get('From', '')
            to = msg.get('To', '')
            date_str = msg.get('Date', '')
            message_id = msg.get('Message-ID', '')
            
            # Parse date
            try:
                date_sent = email.utils.parsedate_to_datetime(date_str)
            except:
                date_sent = datetime.now()
            
            # Extract body
            body_text = ""
            body_html = ""
            attachments = []
            
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    
                    if content_type == "text/plain":
                        body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif content_type == "text/html":
                        body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif part.get_filename():
                        # Attachment
                        attachments.append({
                            'filename': part.get_filename(),
                            'content_type': content_type,
                            'size': len(part.get_payload())
                        })
            else:
                content_type = msg.get_content_type()
                if content_type == "text/plain":
                    body_text = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                elif content_type == "text/html":
                    body_html = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            return {
                'uid': uid,
                'message_id': message_id,
                'subject': subject,
                'sender_email': sender,
                'sender_name': sender,  # Would parse name separately
                'to_addresses': [{'email': to, 'name': ''}],
                'body_text': body_text,
                'body_html': body_html,
                'attachments': attachments,
                'date_sent': date_sent,
                'size': len(str(msg))
            }
            
        except Exception as e:
            logger.error(f"Error parsing email message: {str(e)}")
            return {}
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
