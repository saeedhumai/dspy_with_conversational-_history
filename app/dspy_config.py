"""
DSPy configuration and management module.
Handles the setup and execution of the Chain of Thought model for conversation processing.
Includes classes for conversation management and context creation.
"""

import dspy
import os
import logging
from typing import List
from .models import Message

# Set up module-level logging
logger = logging.getLogger(__name__)

class ConversationalCoT(dspy.Module):
    """
    Chain of Thought conversation processor using DSPy.
    Handles the processing of messages with context awareness.
    """
    
    def __init__(self):
        """Initialize the Chain of Thought module with input/output signature"""
        super().__init__()
        # Define the chain with context and question inputs, answer output
        self.chain = dspy.ChainOfThought("context, question -> answer")
    
    def forward(self, context: str, question: str):
        """
        Process the conversation with full context history
        Args:
            context: String containing all previous conversation messages
            question: Current user's question to process
        Returns:
            Chain of Thought processed response
        """
        # Create a comprehensive prompt that includes all context
        full_prompt = f"""
        Previous conversation:
        {context}
        
        Current question: {question}
        
        Please consider all previous context when responding.
        """
        # Process through Chain of Thought and return result
        return self.chain(
            context=full_prompt,
            question=question
        )

def create_context_from_messages(messages: List[Message]) -> str:
    """
    Create a comprehensive context string from all conversation messages
    Args:
        messages: List of Message objects from the conversation
    Returns:
        Formatted string containing all messages with roles
    """
    context_parts = []
    for msg in messages:
        # Format each message with its role and content
        context_parts.append(f"{msg.role}: {msg.content}")
    
    # Join all messages with newlines
    return "\n".join(context_parts)

class DSPyManager:
    """
    Manages DSPy configuration, model initialization, and message processing.
    Handles the lifecycle of the language model and conversation processing.
    """
    
    def __init__(self):
        """
        Initialize DSPy manager with language model and settings
        Raises:
            ValueError: If OPENAI_API_KEY is not set
            Exception: For any other initialization errors
        """
        # Verify API key exists in environment
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        try:
            # Initialize the GPT-4-mini language model
            self.lm = dspy.LM("openai/gpt-4o-mini")
            # Configure DSPy with model and concurrency settings
            dspy.settings.configure(lm=self.lm, async_max_workers=4)
            # Create Chain of Thought processor and make it async-compatible
            self.cot = ConversationalCoT()
            self.program = dspy.asyncify(self.cot)
            logger.info("DSPy manager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing DSPy manager: {e}")
            raise
    
    async def process_message(self, messages: List[Message], current_message: str):
        """
        Process a message using the full conversation history
        Args:
            messages: List of all previous messages in the conversation
            current_message: The new message to process
        Returns:
            str: The AI-generated response or error message
        """
        try:
            # Create context string from all previous messages
            full_context = create_context_from_messages(messages)
            
            # Log context length for debugging
            logger.info(f"Processing with full context length: {len(full_context)}")
            
            # Process through DSPy and get response
            result = await self.program(
                context=full_context,
                question=current_message
            )
            
            return result.answer
            
        except Exception as e:
            # Log and return user-friendly error message
            logger.error(f"Error processing message: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
        


        