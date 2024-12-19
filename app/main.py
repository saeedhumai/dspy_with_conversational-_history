from fastapi import FastAPI, HTTPException
from .models import ChatRequest
from .storage import ConversationStorage
from .dspy_config import DSPyManager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Conversational DSPy API",
    description="A conversational API using DSPy Chain of Thought",
    version="1.0.0"
)

# Initialize our storage and DSPy manager
try:
    storage = ConversationStorage()
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
    Process a chat message and return the response
    """
    logger.info(f"Received chat request: {request}")
    
    try:
        # Get or create conversation
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
            conversation = storage.create_conversation()
            logger.info(f"Created new conversation: {conversation.id}")
        
        # Add user message to conversation
        user_message = storage.add_message(
            conversation.id,
            "user",
            request.message
        )
        logger.info(f"Added user message to conversation: {user_message}")
        
        # Process message with DSPy
        logger.info("Processing message with DSPy...")
        response = await dspy_manager.process_message(
            conversation.messages,
            request.message
        )
        logger.info(f"Received DSPy response: {response}")
        
        # Add assistant's response to conversation
        assistant_message = storage.add_message(
            conversation.id,
            "assistant",
            response
        )
        logger.info(f"Added assistant response to conversation: {assistant_message}")
        
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
        # Re-raise HTTP exceptions
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