# DSPy Chain of Thought API

FastAPI service implementing Chain of Thought reasoning using DSPy and GPT-4-mini.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set OpenAI API key in `.env`:
```
OPENAI_API_KEY=your_key_here
```

## Run

Start server:
```bash
python run.py
```
Server runs at `http://localhost:8000`

## API Endpoints

### POST /chat
Process messages with conversation history.
for first conversation its important to run it emtpy without conversational id then it will generate conversational id after that put that conversational id and use it for conversation 
Request:
```json
{
    "conversation_id": "optional-id",
    "message": "Your question"
}
```

Response:
```json
{
    "status": "success",
    "conversation_id": "uuid",
    "response": "AI response",
    "history": [
        {
            "role": "user/assistant",
            "content": "message",
            "timestamp": "UTC time"
        }
    ]
}
```

### GET /conversation/{conversation_id}
Retrieve conversation history

### DELETE /conversation/{conversation_id}
Delete a conversation

### GET /health
Check API status