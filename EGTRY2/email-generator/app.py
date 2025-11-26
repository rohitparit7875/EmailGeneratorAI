import os
import json
import time
import requests
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# --- Configuration ---
# API endpoint for the Gemini model
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"
MAX_RETRIES = 5
API_KEY = "" # The execution environment will handle API key injection.

app = Flask(__name__)
# Enable CORS for communication between frontend and backend
CORS(app)

def generate_content_with_retry(prompt_text, system_instruction):
    """
    Calls the Gemini API with exponential backoff for resilience.
    """
    headers = {
        'Content-Type': 'application/json',
    }

    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        # Omit tools, as we are only doing text generation
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status() # Raise exception for 4xx/5xx status codes
            
            result = response.json()
            
            # Safely extract the generated text from the model response
            if result and 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content'] and len(candidate['content']['parts']) > 0:
                    return candidate['content']['parts'][0]['text']

            return "Error: Model returned an empty response or unexpected structure.", 500

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                # Exponential backoff: wait 2^attempt seconds
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                return f"Error: Failed to connect to API after {MAX_RETRIES} attempts. {e}", 503

    return "Error: Maximum retries reached.", 503

@app.route('/')
def serve_index():
    """Serves the main HTML file from the templates folder."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_email():
    """
    Endpoint that handles the email generation request:
    1. Reads topic and tone from the frontend.
    2. Constructs the prompt and system instruction.
    3. Calls the Gemini API.
    4. Parses the response into Subject and Body.
    5. Returns the structured email to the frontend.
    """
    data = request.json
    topic = data.get('topic', '')
    tone = data.get('tone', 'professional')

    if not topic:
        return jsonify({"error": "Please provide content for the email."}), 400

    # Instruct the model clearly how to format the output
    user_prompt = f"Write an email about the following topic: '{topic}'. The required tone should be: {tone}. Start the response with 'Subject:'"
    
    # System instruction enforces the model's behavior
    system_instruction = "You are a professional email assistant. Your task is to generate a well-structured, complete email based on the user's request. The output must start with 'Subject:' followed by a suitable subject line, and then the email body. Do not include any introductory or concluding text outside of the email content itself, and make sure to include a closing (e.g., 'Best regards,')."

    generated_text = generate_content_with_retry(user_prompt, system_instruction)
    
    if isinstance(generated_text, tuple):
        # Handle error case from the retry function
        error_message, status_code = generated_text
        return jsonify({"error": error_message}), status_code

    # Parsing the output into subject and body based on the 'Subject:' prefix
    email_lines = generated_text.split('\n')
    subject = "No Subject Provided"
    body = generated_text
    
    if email_lines and email_lines[0].lower().startswith('subject:'):
        subject = email_lines[0].replace('Subject:', '').strip()
        body = '\n'.join(email_lines[1:]).strip() # Everything after the subject is the body

    return jsonify({
        "subject": subject,
        "body": body
    })

if __name__ == '__main__':
    # Flask requires the template folder structure
    if not os.path.exists('templates'):
        os.makedirs('templates')
    # Use 0.0.0.0 to make it accessible outside localhost if necessary
    # app.run(host='0.0.0.0', port=5000, debug=True)
    pass