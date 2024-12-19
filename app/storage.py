# app/storage.py
from typing import Dict, Optional
from .models import Conversation, Message

class ConversationStorage:
    def __init__(self):
        # Initialize empty dictionary for storing conversations
        self._conversations: Dict[str, Conversation] = {}
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        return self._conversations.get(conversation_id)
    
    def create_conversation(self) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation()
        self._conversations[conversation.id] = conversation
        return conversation
    
    def add_message(self, conversation_id: str, role: str, content: str) -> Optional[Message]:
        """Add a message to a conversation"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            message = conversation.add_message(role, content)
            return message
        return None

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            return True
        return False