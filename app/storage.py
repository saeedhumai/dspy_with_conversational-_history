# app/storage.py
"""
In-memory storage management for conversations.
Handles creating, retrieving, and deleting conversations and their messages.
"""

from typing import Dict, Optional
from .models import Conversation, Message

class ConversationStorage:
    """
    Manages in-memory storage of conversations
    Provides methods for CRUD operations on conversations and messages
    """
    
    def __init__(self):
        """Initialize empty storage for conversations"""
        self._conversations: Dict[str, Conversation] = {}
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Retrieve a conversation by its ID
        Args:
            conversation_id: Unique identifier of the conversation
        Returns:
            Conversation object if found, None otherwise
        """
        return self._conversations.get(conversation_id)
    
    def create_conversation(self) -> Conversation:
        """
        Create a new conversation
        Returns:
            Newly created Conversation object
        """
        conversation = Conversation()
        self._conversations[conversation.id] = conversation
        return conversation
    
    def add_message(self, conversation_id: str, role: str, content: str) -> Optional[Message]:
        """
        Add a message to an existing conversation
        Args:
            conversation_id: ID of the target conversation
            role: Message sender ('user' or 'assistant')
            content: Message content
        Returns:
            Created Message object if successful, None if conversation not found
        """
        conversation = self.get_conversation(conversation_id)
        if conversation:
            message = conversation.add_message(role, content)
            return message
        return None

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation from storage
        Args:
            conversation_id: ID of conversation to delete
        Returns:
            True if deleted successfully, False if not found
        """
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            return True
        return False