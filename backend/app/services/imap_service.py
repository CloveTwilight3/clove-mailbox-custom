import imaplib
import email
import email.utils
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
import re

from app.schemas.email import EmailCreate
from app.schemas.account import EmailAccount

logger = logging.getLogger(__name__)


class IMAPService:
    def __init__(self, account: EmailAccount, password: str):
        self.account = account
        self.password = password
        self.connection = None
        self.current_folder = None
        
    def connect(self) -> bool:
        """Connect to IMAP server"""
        try:
            logger.info(f"Connecting to IMAP server {self.account.imap_host}:{self.account.imap_port}")
            
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
            
            logger.info(f"Attempting login for user: {self.account.imap_username}")
            self.connection.login(self.account.imap_username, self.password)
            logger.info(f"Successfully connected to IMAP server for {self.account.email_address}")
            return True
            
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP error connecting to server: {str(e)}")
            return False
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
            self.current_folder = None
    
    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """Test IMAP connection"""
        try:
            if self.connect():
                # Test selecting a folder
                if self.select_folder("INBOX"):
                    self.disconnect()
                    return True, None
                else:
                    self.disconnect()
                    return False, "Could not select INBOX folder"
            return False, "Failed to connect"
        except Exception as e:
            return False, str(e)
    
    def get_folders(self) -> List[str]:
        """Get list of available folders"""
        if not self.connection:
            if not self.connect():
                return ["INBOX"]
            
        try:
            status, folders = self.connection.list()
            folder_list = []
            
            if status == 'OK':
                for folder in folders:
                    # Parse folder name from IMAP response
                    folder_str = folder.decode() if isinstance(folder, bytes) else folder
                    # Extract folder name from response like: (\HasNoChildren) "." "INBOX"
                    parts = folder_str.split('"')
                    if len(parts) >= 3:
                        folder_name = parts[-2]
                        folder_list.append(folder_name)
                    
            return folder_list or ["INBOX"]
        except Exception as e:
            logger.error(f"Error getting folders: {str(e)}")
            return ["INBOX"]
    
    def select_folder(self, folder: str = "INBOX") -> bool:
        """Select a folder - CRITICAL FIX"""
        if not self.connection:
            if not self.connect():
                logger.error("Cannot select folder: not connected to IMAP server")
                return False
            
        try:
            logger.info(f"Selecting folder: {folder}")
            status, messages = self.connection.select(folder)
            if status == 'OK':
                self.current_folder = folder
                logger.info(f"Successfully selected folder: {folder}")
                return True
            else:
                logger.error(f"Failed to select folder {folder}: {status}")
                return False
        except Exception as e:
            logger.error(f"Error selecting folder {folder}: {str(e)}")
            return False
    
    def ensure_folder_selected(self, folder: str = "INBOX") -> bool:
        """Ensure the correct folder is selected before any operations"""
        if self.current_folder != folder:
            return self.select_folder(folder)
        return True
    
    def get_email_list(self, folder: str = "INBOX", limit: int = 50) -> List[Dict]:
        """Get list of emails from folder"""
        if not self.ensure_folder_selected(folder):
            logger.error(f"Failed to select folder: {folder}")
            return []
            
        try:
            # Search for all emails
            status, messages = self.connection.search(None, 'ALL')
            
            if status != 'OK':
                logger.error(f"IMAP search failed with status: {status}")
                return []
            
            if not messages or not messages[0]:
                logger.info(f"No emails found in folder: {folder}")
                return []
            
            email_ids = messages[0].split()
            email_list = []
            
            if not email_ids:
                logger.info(f"No email IDs found in folder: {folder}")
                return []
            
            # Get the most recent emails (reverse order)
            recent_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            recent_ids.reverse()
            
            logger.info(f"Processing {len(recent_ids)} emails from folder {folder}")
            
            processed_count = 0
            for email_id in recent_ids:
                try:
                    email_data = self._fetch_email_headers(email_id)
                    if email_data:
                        email_list.append(email_data)
                        processed_count += 1
                    else:
                        logger.debug(f"Skipped email {email_id} - no data returned")
                except Exception as e:
                    logger.warning(f"Error processing email {email_id}: {str(e)}")
                    continue
            
            logger.info(f"Successfully processed {processed_count} out of {len(recent_ids)} emails")
            return email_list
            
        except Exception as e:
            logger.error(f"Error getting email list from folder {folder}: {str(e)}")
            return []
    
    def get_email_content(self, uid: str, folder: str = "INBOX") -> Optional[Dict]:
        """Get full email content by UID - FIXED VERSION"""
        # Ensure we're connected and have the right folder selected
        if not self.ensure_folder_selected(folder):
            logger.error(f"Failed to select folder {folder} for UID {uid}")
            return None
            
        try:
            logger.info(f"Fetching email content for UID {uid} in folder {folder}")
            
            # Fetch the complete email
            status, msg_data = self.connection.fetch(uid, '(RFC822)')
            
            if status != 'OK' or not msg_data or not msg_data[0]:
                logger.warning(f"Failed to fetch email content for UID {uid}: status={status}")
                return None
                
            email_body = msg_data[0][1]
            if not email_body:
                logger.warning(f"No email body data for UID {uid}")
                return None
                
            # Parse the email message
            email_message = email.message_from_bytes(email_body)
            parsed_data = self._parse_email_message(email_message, uid)
            
            # Also get flags to see if it's read
            try:
                flag_status, flag_data = self.connection.fetch(uid, '(FLAGS)')
                if flag_status == 'OK' and flag_data:
                    flags_line = flag_data[0][0].decode() if isinstance(flag_data[0][0], bytes) else str(flag_data[0][0])
                    parsed_data['is_read'] = '\\Seen' in flags_line
            except Exception as e:
                logger.debug(f"Could not fetch flags for UID {uid}: {e}")
                parsed_data['is_read'] = False
            
            logger.info(f"Successfully fetched email content for UID {uid}")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error getting email content for UID {uid}: {str(e)}")
            return None
    
    def mark_as_read(self, uid: str, folder: str = "INBOX") -> bool:
        """Mark email as read"""
        if not self.ensure_folder_selected(folder):
            return False
            
        try:
            self.connection.store(uid, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"Error marking email as read: {str(e)}")
            return False
    
    def mark_as_unread(self, uid: str, folder: str = "INBOX") -> bool:
        """Mark email as unread"""
        if not self.ensure_folder_selected(folder):
            return False
            
        try:
            self.connection.store(uid, '-FLAGS', '\\Seen')
            return True
        except Exception as e:
            logger.error(f"Error marking email as unread: {str(e)}")
            return False
    
    def delete_email(self, uid: str, folder: str = "INBOX") -> bool:
        """Delete email"""
        if not self.ensure_folder_selected(folder):
            return False
            
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
            # Convert email_id to string if it's bytes
            if isinstance(email_id, bytes):
                email_id_str = email_id.decode()
            else:
                email_id_str = str(email_id)
            
            # Fetch basic info first
            status, msg_data = self.connection.fetch(email_id, '(FLAGS RFC822.HEADER)')
            
            if status != 'OK' or not msg_data or len(msg_data) < 1:
                logger.warning(f"Failed to fetch email {email_id_str}: {status}")
                return None
            
            # Parse flags from the response
            is_read = False
            try:
                # The response format is usually: b'1 (FLAGS (\\Seen) RFC822.HEADER {size}'
                response_line = ""
                if msg_data[0] and len(msg_data[0]) > 0:
                    if isinstance(msg_data[0][0], bytes):
                        response_line = msg_data[0][0].decode('utf-8', errors='ignore')
                    elif msg_data[0][0] is not None:
                        response_line = str(msg_data[0][0])
                
                if '\\Seen' in response_line:
                    is_read = True
            except Exception as e:
                logger.debug(f"Could not parse flags for email {email_id_str}: {e}")
            
            # Parse email headers
            try:
                # Get the actual email header data
                header_data = None
                if len(msg_data[0]) > 1 and msg_data[0][1]:
                    header_data = msg_data[0][1]
                elif len(msg_data) > 1 and msg_data[1] and len(msg_data[1]) > 1:
                    header_data = msg_data[1][1]
                
                if not header_data:
                    logger.warning(f"No header data found for email {email_id_str}")
                    return None
                
                # Parse email message
                if isinstance(header_data, bytes):
                    email_message = email.message_from_bytes(header_data)
                else:
                    email_message = email.message_from_string(str(header_data))
                
                # Parse sender
                sender_raw = email_message.get('From', 'unknown@unknown.com')
                try:
                    sender_name, sender_email = email.utils.parseaddr(sender_raw)
                    if not sender_email:
                        sender_email = sender_raw
                    if not sender_name:
                        sender_name = sender_email
                except:
                    sender_email = sender_raw
                    sender_name = sender_raw
                
                # Parse date
                date_received = datetime.now()
                date_str = email_message.get('Date', '')
                if date_str:
                    try:
                        date_received = email.utils.parsedate_to_datetime(date_str)
                    except Exception as e:
                        logger.debug(f"Could not parse date '{date_str}': {e}")
                
                # Parse subject
                subject = email_message.get('Subject', '(No Subject)')
                if subject and subject != '(No Subject)':
                    try:
                        # Decode subject if it's encoded
                        decoded_header = email.header.decode_header(subject)
                        subject_parts = []
                        for part, encoding in decoded_header:
                            if isinstance(part, bytes):
                                try:
                                    decoded_part = part.decode(encoding or 'utf-8', errors='ignore')
                                    subject_parts.append(decoded_part)
                                except:
                                    subject_parts.append(part.decode('utf-8', errors='ignore'))
                            else:
                                subject_parts.append(str(part))
                        subject = ''.join(subject_parts)
                    except Exception as e:
                        logger.debug(f"Could not decode subject: {e}")
                        # Keep original subject if decoding fails
                
                # Get message ID
                message_id = email_message.get('Message-ID', f'<local-{email_id_str}@{self.account.email_address}>')
                
                return {
                    'uid': email_id_str,
                    'message_id': message_id,
                    'subject': subject,
                    'sender_email': sender_email,
                    'sender_name': sender_name,
                    'date_received': date_received,
                    'is_read': is_read,
                    'size': len(header_data) if header_data else 0,
                    'folder': self.current_folder or 'INBOX'
                }
                
            except Exception as e:
                logger.error(f"Error parsing email headers for {email_id_str}: {str(e)}")
                # Return a basic email record even if parsing fails
                return {
                    'uid': email_id_str,
                    'message_id': f'<error-{email_id_str}@{self.account.email_address}>',
                    'subject': f'Email {email_id_str} (parsing error)',
                    'sender_email': 'unknown@unknown.com',
                    'sender_name': 'Unknown Sender',
                    'date_received': datetime.now(),
                    'is_read': is_read,
                    'size': 0,
                    'folder': self.current_folder or 'INBOX'
                }
            
        except Exception as e:
            logger.error(f"Error fetching email headers for {email_id}: {str(e)}")
            return None
    
    def _parse_email_message(self, msg: email.message.Message, uid: str) -> Dict:
        """Parse email message into structured data"""
        try:
            # Extract basic info
            subject = msg.get('Subject', '')
            if subject:
                # Decode subject if it's encoded
                decoded_header = email.header.decode_header(subject)
                subject = ""
                for part, encoding in decoded_header:
                    if isinstance(part, bytes):
                        subject += part.decode(encoding or 'utf-8', errors='ignore')
                    else:
                        subject += part
            
            # Parse sender
            sender_raw = msg.get('From', '')
            sender_name, sender_email = email.utils.parseaddr(sender_raw)
            sender_email = sender_email or sender_raw
            
            # Parse recipients
            to_raw = msg.get('To', '')
            to_addresses = []
            if to_raw:
                to_list = email.utils.getaddresses([to_raw])
                to_addresses = [{'name': name, 'email': addr} for name, addr in to_list if addr]
            
            # Parse date
            date_str = msg.get('Date', '')
            try:
                date_sent = email.utils.parsedate_to_datetime(date_str)
            except:
                date_sent = datetime.now()
            
            message_id = msg.get('Message-ID', f'<local-{uid}>')
            reply_to = msg.get('Reply-To', '')
            
            # Extract body - IMPROVED VERSION
            body_text = ""
            body_html = ""
            attachments = []
            
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get('Content-Disposition', ''))
                    
                    # Skip attachment parts for body extraction
                    if 'attachment' not in content_disposition:
                        if content_type == "text/plain":
                            try:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    charset = part.get_content_charset() or 'utf-8'
                                    body_text = payload.decode(charset, errors='ignore')
                            except Exception as e:
                                logger.debug(f"Error decoding text part: {e}")
                                pass
                        elif content_type == "text/html":
                            try:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    charset = part.get_content_charset() or 'utf-8'
                                    body_html = payload.decode(charset, errors='ignore')
                            except Exception as e:
                                logger.debug(f"Error decoding HTML part: {e}")
                                pass
                    
                    # Handle attachments
                    if part.get_filename() or 'attachment' in content_disposition:
                        filename = part.get_filename() or 'unknown'
                        attachments.append({
                            'filename': filename,
                            'content_type': content_type,
                            'size': len(part.get_payload() or '')
                        })
            else:
                content_type = msg.get_content_type()
                try:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        charset = msg.get_content_charset() or 'utf-8'
                        decoded_payload = payload.decode(charset, errors='ignore')
                        if content_type == "text/plain":
                            body_text = decoded_payload
                        elif content_type == "text/html":
                            body_html = decoded_payload
                        else:
                            body_text = decoded_payload
                except Exception as e:
                    logger.debug(f"Error decoding single part message: {e}")
                    pass
            
            return {
                'uid': uid,
                'message_id': message_id,
                'subject': subject or '(No Subject)',
                'sender_email': sender_email,
                'sender_name': sender_name or sender_email,
                'reply_to': reply_to,
                'to_addresses': to_addresses,
                'body_text': body_text,
                'body_html': body_html,
                'attachments': attachments,
                'date_sent': date_sent,
                'date_received': date_sent,  # Use sent date as received for now
                'size': len(str(msg))
            }
            
        except Exception as e:
            logger.error(f"Error parsing email message: {str(e)}")
            return {
                'uid': uid,
                'message_id': f'<error-{uid}>',
                'subject': 'Error parsing email',
                'sender_email': 'unknown@unknown.com',
                'sender_name': 'Unknown',
                'body_text': f'Error parsing email: {str(e)}',
                'date_sent': datetime.now(),
                'date_received': datetime.now(),
                'size': 0
            }
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
