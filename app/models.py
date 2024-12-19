"""
Data models for the chat application.
Defines the structure for messages, conversations, and API requests.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
import uuid

class Message(BaseModel):
    """
    Represents a single message in a conversation
    Attributes:
        role: Identifier of message sender ('user' or 'assistant')
        content: The actual message text
        timestamp: When the message was created (UTC)
    """
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def __str__(self):
        """String representation of message"""
        return f"{self.role}: {self.content}"

class Conversation(BaseModel):
    """
    Represents a conversation thread containing multiple messages
    Attributes:
        id: Unique identifier for the conversation
        messages: List of messages in the conversation
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = []
    
    def add_message(self, role: str, content: str) -> Message:
        """
        Add a new message to the conversation
        Args:
            role: Message sender ('user' or 'assistant')
            content: Message content
        Returns:
            The created Message object
        """
        message = Message(role=role, content=content)
        self.messages.append(message)
        return message

class ChatRequest(BaseModel):
    """
    Schema for incoming chat API requests
    Attributes:
        conversation_id: Optional ID of existing conversation
        message: The user's message text
    """
    conversation_id: str | None = None
    message: str