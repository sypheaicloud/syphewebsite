from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

# Serve your HTML files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('.', path)
    except:
        return "File not found", 404

# --- CONTACT FORM ---
@app.route('/api/contact', methods=['POST', 'OPTIONS'])
def contact():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400
            
        name = data.get('name', 'Unknown')
        email = data.get('email', 'No Email')
        subject = data.get('subject', 'No Subject')
        message = data.get('message', 'No Message')
        
        api_key = os.getenv("RESEND_API_KEY")
        
        if not api_key:
            return jsonify({"status": "error", "message": "API key not configured"}), 500
        
        print(f"Sending email from: {name} ({email})")
        
        res = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Contact Form <hello@sypheit.cloud>",
                "to": ["sypheit@gmail.com"],
                "subject": f"Contact Form: {subject}",
                "reply_to": email,
                "html": f"""
                    <div style="font-family: sans-serif; line-height: 1.5; color: #333; border: 1px solid #ddd; padding: 20px;">
                        <h2 style="color: #007bff;">New Message from {name}</h2>
                        <p><strong>Email:</strong> {email}</p>
                        <p><strong>Subject:</strong> {subject}</p>
                        <hr>
                        <p><strong>Message:</strong></p>
                        <p style="background: #f9f9f9; padding: 15px;">{message}</p>
                    </div>
                """
            }
        )
        
        print(f"Resend API response status: {res.status_code}")
        print(f"Resend API response: {res.text}")
        
        if res.status_code < 300:
            return jsonify({
                "status": "success",
                "message": "Thank you for your message!"
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Email service error: {res.text}"
            }), 500
    
    except Exception as e:
        print(f"Error in contact route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# --- SUBSCRIBE FORM ---
@app.route('/api/subscribe', methods=['POST', 'OPTIONS'])
def subscribe():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No data received"}), 400
            
        subscriber_email = data.get('email')
        
        if not subscriber_email:
            return jsonify({"error": "Email is required"}), 400
        
        api_key = os.getenv("RESEND_API_KEY")
        
        if not api_key:
            return jsonify({"error": "API key not configured"}), 500
        
        print(f"New subscriber: {subscriber_email}")
        
        # Send welcome email
        welcome_res = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Sypheit Newsletter <newsletter@sypheit.cloud>",
                "to": [subscriber_email],
                "subject": "Welcome to the Family! 🚀",
                "html": """
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
                        <h2 style="color: #007bff;">Thanks for joining!</h2>
                        <p>Hi there,</p>
                        <p>We're thrilled to have you on board. You'll be the first to hear about our latest updates directly from <strong>sypheit.cloud</strong>.</p>
                        <p>Cheers,<br>The Sypheit Team</p>
                    </div>
                """
            }
        )
        
        print(f"Welcome email response: {welcome_res.status_code}")
        print(f"Welcome email response body: {welcome_res.text}")
        
        # Send admin notification
        admin_res = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "System <admin@sypheit.cloud>",
                "to": ["sypheit@gmail.com"],
                "subject": "🔥 New Subscriber Alert!",
                "html": f"<p>New subscriber: <b>{subscriber_email}</b></p>"
            }
        )
        
        print(f"Admin notification response: {admin_res.status_code}")

        # --- ADD SUBSCRIBER TO AUDIENCE ---
        audience_id = "71e1df0e-b4a0-4640-9742-f01f9c373b6e"
        
        add_to_audience = requests.post(
            f"https://api.resend.com/audiences/{audience_id}/contacts",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "email": subscriber_email
            }
        )
        
        print(f"Added to audience: {add_to_audience.status_code}")
        
        if welcome_res.status_code < 300:
            return jsonify({"status": "ok"})
        else:
            raise Exception(f"Resend API error: {welcome_res.text}")
    
    except Exception as e:
        print(f"Error in subscribe route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Local server running on http://localhost:5000")
    print("📧 Make sure RESEND_API_KEY is set in your .env file")
    app.run(debug=True, port=5000)