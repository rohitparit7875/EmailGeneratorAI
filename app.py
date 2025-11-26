from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import openai

# Load your API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class EmailInput(BaseModel):
    purpose: str
    tone: str = "formal"
    length: str = "short"
    recipient_name: str | None = None
    recipient_company: str | None = None
    sender_name: str | None = None
    extra_details: str | None = None

def build_prompt(data):
    return f"""
You are EmailGeneratorAI.
Write a polished email with the following details:

Purpose: {data.purpose}
Tone: {data.tone}
Length: {data.length}
Recipient Name: {data.recipient_name}
Company: {data.recipient_company}
Sender Name: {data.sender_name}
Extra Details: {data.extra_details}

Return the email in this format:

### SUBJECT: <subject>
<body text>
    """

@app.post("/generate")
def generate_email(data: EmailInput):

    prompt = build_prompt(data)

    # Call the OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "system", "content": "You write clean professional emails."},
            {"role": "user", "content": prompt}
        ]
    )

    output = response['choices'][0]['message']['content']

    # Parse subject + body
    if "### SUBJECT:" in output:
        parts = output.split("### SUBJECT:")[1].strip().split("\n", 1)
        subject = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ""
    else:
        # fallback
        lines = output.splitlines()
        subject = lines[0]
        body = "\n".join(lines[1:])

    return {
        "subject": subject,
        "body": body
    }
