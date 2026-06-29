from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# Absolute path fix (prevents template errors)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Request model
class EmailRequest(BaseModel):
    prompt: str
    tone: str = "formal"


# Home route (API check)
@app.get("/")
def home():
    return {"message": "AI Email Generator Running 🚀"}


# UI route (HTML page)
from fastapi.responses import FileResponse

@app.get("/ui")
def ui():
    return FileResponse("templates/index.html")

# Generate email using Groq AI
@app.post("/generate")
def generate_email(request: EmailRequest):

    try:
        from groq import Groq

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            return {"error": "API key missing"}

        client = Groq(api_key=api_key)

        tone_instructions = {
            "formal": "Write a professional formal email.",
            "friendly": "Write a friendly casual email.",
            "cold": "Write a short cold outreach email."
        }

        instruction = tone_instructions.get(request.tone, "formal")

        full_prompt = f"{instruction}\n\n{request.prompt}"

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an email writing assistant."},
                {"role": "user", "content": full_prompt}
            ]
        )

        return {
            "success": True,
            "email": response.choices[0].message.content
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }