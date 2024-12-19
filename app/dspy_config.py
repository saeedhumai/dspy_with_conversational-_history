# app/dspy_config.py
import dspy
import os
import logging
logger = logging.getLogger(__name__)
class ConversationalCoT(dspy.Module):
    """DSPy module for handling conversational interactions"""
    def __init__(self):
        super().__init__()
        # Define our chain of thought with context
        self.chain = dspy.ChainOfThought("context, question -> answer")
    
    def forward(self, context: str, question: str):
        """Process a question with context and return an answer"""
        return self.chain(
            context=context,
            question=question
        )

def create_context_from_messages(messages, max_messages=5):
    """Create context string from recent messages"""
    recent_messages = messages[-max_messages:]
    return "\n".join(str(msg) for msg in recent_messages)

class DSPyManager:
    """Manages DSPy configuration and processing"""
    
    def __init__(self):
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        try:
            # Initialize language model
            self.lm = dspy.LM("openai/gpt-4o-mini")
            # Configure DSPy settings
            dspy.settings.configure(lm=self.lm, async_max_workers=4)
            # Create and asyncify the program
            self.cot = ConversationalCoT()  # Create instance first
            self.program = dspy.asyncify(self.cot)  # Then asyncify it
            logger.info("DSPy manager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing DSPy manager: {e}")
            raise
    
    async def process_message(self, messages, current_message):
        """Process a message with conversation history"""
        try:
            context = create_context_from_messages(messages)
            result = await self.program(
                context=context,
                question=current_message
            )
            return result.answer
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
        

        