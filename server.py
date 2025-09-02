from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from chatbot import app  # import your chatbot workflow

app_api = FastAPI()

# Allow React frontend to talk with Python backend
app_api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app_api.post("/chat")
def chat_endpoint(req: ChatRequest):
    initial_state = {
        "messages": [HumanMessage(content=req.message)],
        "next_node": "router"
    }
    final_state = app.invoke(initial_state)
    last_bot_message = final_state['messages'][-1]
    return {"reply": last_bot_message.content}

@app_api.get("/chat")
def chat_get():
    return {"message": "This endpoint only accepts POST requests. Please use POST method."}

@app_api.get("/")
def health_check():
    return {"status": "healthy", "message": "WaterWise Bot API is running"}
