"""
Main FastAPI application file that handles all HTTP endpoints and routing.
Manages chat conversations and integrates with DSPy for processing messages.
"""

from fastapi import FastAPI, HTTPException
from .models import ChatRequest
from .storage import ConversationStorage
from .dspy_config import DSPyManager
import logging

# Configure logging with timestamp, logger name, level and message
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Conversational DSPy API",
    description="A conversational API using DSPy Chain of Thought",
    version="1.0.0"
)

# Initialize core services
try:
    # Create storage instance for managing conversations
    storage = ConversationStorage()
    # Create DSPy manager for handling AI processing
    dspy_manager = DSPyManager()
    logger.info("Successfully initialized storage and DSPy manager")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    raise

@app.get("/")
async def root():
    """Root endpoint for API health check"""
    return {"status": "active", "message": "Conversational DSPy API is running"}

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Process a chat message and return the response.
    Handles conversation management and message processing through DSPy.
    """
    logger.info(f"Received chat request: {request}")
    
    try:
        # Check if conversation exists or create new one
        if request.conversation_id:
            conversation = storage.get_conversation(request.conversation_id)
            if not conversation:
                logger.warning(f"Conversation not found: {request.conversation_id}")
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found"
                )
            logger.info(f"Retrieved existing conversation: {request.conversation_id}")
        else:
            # Create new conversation if no ID provided
            conversation = storage.create_conversation()
            logger.info(f"Created new conversation: {conversation.id}")
        
        # Store user's message in conversation history
        user_message = storage.add_message(
            conversation.id,
            "user",
            request.message
        )
        logger.info(f"Added user message to conversation: {user_message}")
        
        # Process message using DSPy AI model
        logger.info("Processing message with DSPy...")
        response = await dspy_manager.process_message(
            conversation.messages,
            request.message
        )
        logger.info(f"Received DSPy response: {response}")
        
        # Store AI's response in conversation history
        assistant_message = storage.add_message(
            conversation.id,
            "assistant",
            response
        )
        logger.info(f"Added assistant response to conversation: {assistant_message}")
        
        # Return complete response with conversation history
        return {
            "status": "success",
            "conversation_id": conversation.id,
            "response": response,
            "history": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in conversation.messages
            ]
        }
        
    except HTTPException as e:
        # Re-raise HTTP exceptions for proper error handling
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Retrieve the history of a conversation
    """
    logger.info(f"Retrieving conversation: {conversation_id}")
    
    try:
        conversation = storage.get_conversation(conversation_id)
        if not conversation:
            logger.warning(f"Conversation not found: {conversation_id}")
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
        
        return {
            "conversation_id": conversation.id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in conversation.messages
            ]
        }
        
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving the conversation: {str(e)}"
        )

@app.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation
    """
    logger.info(f"Deleting conversation: {conversation_id}")
    
    try:
        success = storage.delete_conversation(conversation_id)
        if not success:
            logger.warning(f"Conversation not found for deletion: {conversation_id}")
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
        
        logger.info(f"Successfully deleted conversation: {conversation_id}")
        return {
            "status": "success",
            "message": "Conversation deleted successfully"
        }
        
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while deleting the conversation: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify service status
    """
    return {
        "status": "healthy",
        "storage": "operational",
        "dspy": "operational"
    }