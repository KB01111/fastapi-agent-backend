
"""
Gmail Integration Module

This module provides functionality to connect to and interact with Gmail,
allowing the application to send emails and access Gmail data.
"""

import asyncio
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List, Union
import structlog
from pydantic import BaseModel

logger = structlog.get_logger(__name__)

class GmailConfig(BaseModel):
    """Configuration for Gmail API connection."""
    client_id: str
    client_secret: str
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    token_uri: str = "https://oauth2.googleapis.com/token"
    scopes: List[str] = ["https://www.googleapis.com/auth/gmail.send", 
                         "https://www.googleapis.com/auth/gmail.readonly"]

class EmailMessage(BaseModel):
    """Email message model."""
    to: Union[str, List[str]]
    subject: str
    body: str
    body_type: str = "html"  # "html" or "plain"
    cc: Optional[Union[str, List[str]]] = None
    bcc: Optional[Union[str, List[str]]] = None
    reply_to: Optional[str] = None

class GmailClient:
    """Client for interacting with Gmail API."""
    
    def __init__(self, config: GmailConfig):
        self.config = config
        self.service = None
        self.available = False
        self._initialize()
    
    def _initialize(self):
        """Initialize the Gmail API client."""
        try:
            # Try to import the required libraries
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
                self.Credentials = Credentials
                self.build = build
            except ImportError:
                logger.warning("Google API libraries not installed.")
                return
            
            # Create credentials
            creds = self.Credentials(
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
                refresh_token=self.config.refresh_token,
                token_uri=self.config.token_uri,
                scopes=self.config.scopes
            )
            
            # Build the Gmail service
            self.service = self.build('gmail', 'v1', credentials=creds)
            self.available = True
            logger.info("Gmail client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Gmail client: {e}")
            self.available = False
    
    def _create_message(self, email: EmailMessage) -> Dict[str, Any]:
        """
        Create a message for the Gmail API.
        
        Args:
            email: Email message details
            
        Returns:
            Dict containing the raw message
        """
        message = MIMEMultipart()
        
        # Convert to list if string
        to_list = [email.to] if isinstance(email.to, str) else email.to
        message["To"] = ", ".join(to_list)
        
        message["Subject"] = email.subject
        
        if email.cc:
            cc_list = [email.cc] if isinstance(email.cc, str) else email.cc
            message["Cc"] = ", ".join(cc_list)
            
        if email.bcc:
            bcc_list = [email.bcc] if isinstance(email.bcc, str) else email.bcc
            message["Bcc"] = ", ".join(bcc_list)
            
        if email.reply_to:
            message["Reply-To"] = email.reply_to
        
        # Attach body
        if email.body_type.lower() == "html":
            message.attach(MIMEText(email.body, "html"))
        else:
            message.attach(MIMEText(email.body, "plain"))
        
        # Encode message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        return {"raw": encoded_message}
    
    async def send_email(self, email: EmailMessage) -> Dict[str, Any]:
        """
        Send an email using Gmail API.
        
        Args:
            email: Email message to send
            
        Returns:
            Dict containing the result of the operation
        """
        if not self.available:
            return {"error": "Gmail client not available"}
        
        try:
            # Create message
            message = self._create_message(email)
            
            # Send message in a separate thread
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.service.users().messages().send(
                    userId="me", body=message
                ).execute()
            )
            
            logger.info("Email sent successfully", message_id=result.get("id"))
            return {"success": True, "message_id": result.get("id")}
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {"error": str(e)}
    
    async def get_messages(self, query: str = "", max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get messages from Gmail.
        
        Args:
            query: Gmail search query
            max_results: Maximum number of results to return
            
        Returns:
            List of messages
        """
        if not self.available:
            return []
        
        try:
            # List messages in a separate thread
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.service.users().messages().list(
                    userId="me", q=query, maxResults=max_results
                ).execute()
            )
            
            messages = result.get("messages", [])
            
            # Get message details
            detailed_messages = []
            for msg in messages:
                msg_id = msg["id"]
                message = await loop.run_in_executor(
                    None,
                    lambda: self.service.users().messages().get(
                        userId="me", id=msg_id
                    ).execute()
                )
                detailed_messages.append(message)
            
            return detailed_messages
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []

# Factory function to create a client with configuration
def create_gmail_client(
    client_id: str,
    client_secret: str,
    refresh_token: Optional[str] = None,
    access_token: Optional[str] = None
) -> GmailClient:
    """
    Create a Gmail client with the given configuration.
    
    Args:
        client_id: Google OAuth client ID
        client_secret: Google OAuth client secret
        refresh_token: OAuth refresh token
        access_token: OAuth access token
        
    Returns:
        GmailClient instance
    """
    config = GmailConfig(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        access_token=access_token
    )
    return GmailClient(config)