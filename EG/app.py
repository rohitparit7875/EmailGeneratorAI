from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Route to serve the frontend HTML file
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint that the JavaScript calls
@app.route('/generate', methods=['POST'])
def generate_email():
    data = request.get_json()
    
    # --- 1. Get Inputs from Frontend ---
    recipient = data.get('recipient')
    email_type = data.get('emailType')
    keywords = data.get('keywords')
    
    # --- 2. Your Python Generation Logic Goes Here ---
    # This is where you would use Jinja2, OpenAI API, NLTK, etc.
    
    # Simple placeholder logic for demonstration:
    if email_type == 'followup':
        subject = f"Following up: {keywords}"
        body = f"Hi {recipient},\n\nI hope this email finds you well. I'm following up on our discussion regarding {keywords}. I'd love to show you how our solution can help.\n\nBest regards,\n[Your Name]"
    else:
        subject = f"Generated Email for {recipient}"
        body = f"Hello {recipient},\n\nThis is a standard generated email for the purpose of '{email_type}' with the key details: '{keywords}'.\n\n[Your Email Generator Content Here]\n\nThank you,\n[Your Name]"

    full_email_output = f"Subject: {subject}\n\n{body}"

    # --- 3. Return the result back to the Frontend ---
    return jsonify({'email': full_email_output})

if __name__ == '__main__':
    app.run(debug=True)