from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
import uuid

class Message(BaseModel):
    """Single message in a conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def __str__(self):
        return f"{self.role}: {self.content}"

class Conversation(BaseModel):
    """Conversation containing multiple messages"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = []
    
    def add_message(self, role: str, content: str) -> Message:
        """Helper method to add a new message"""
        message = Message(role=role, content=content)
        self.messages.append(message)
        return message

class ChatRequest(BaseModel):
    """Incoming chat request"""
    conversation_id: str | None = None
    message: str