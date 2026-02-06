from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import parse_qs

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Allow browsers to check the API before sending data
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        # CORS Header for the actual POST response
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        
        # 1. Read the incoming data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        # 2. Parse the data based on Content-Type
        content_type = self.headers.get('Content-Type', '')
        
        try:
            if 'application/json' in content_type:
                data = json.loads(post_data)
            else:
                parsed_data = parse_qs(post_data)
                data = {k: v[0] for k, v in parsed_data.items()}
        except Exception as e:
            print(f"Error parsing data: {e}")
            data = {}

        # 3. Extract form fields
        name = data.get('name', 'Unknown')
        user_email = data.get('email', 'No Email')
        subject = data.get('subject', 'No Subject')
        message = data.get('message', 'No Message')

        # 4. Get API Key
        api_key = os.environ.get("RESEND_API_KEY")
        
        # 5. Send the email via Resend
        res = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                # CHANGED: Sent FROM your new professional support email
                "from": f"Sypheit Support <support@sypheit.cloud>", 
                # CHANGED: Sent TO your support email (which Cloudflare forwards to your Gmail)
                "to": ["support@sypheit.cloud"], 
                "subject": f"New Contact Form Message: {subject}",
                # IMPORTANT: This lets you reply directly to the person who filled the form
                "reply_to": user_email, 
                "html": f"""
                    <div style="font-family: sans-serif; line-height: 1.5; color: #333; border: 1px solid #ddd; padding: 20px;">
                        <h2 style="color: #007bff;">New Message from {name}</h2>
                        <p><strong>Visitor Email:</strong> {user_email}</p>
                        <p><strong>Subject:</strong> {subject}</p>
                        <hr style="border: none; border-top: 1px solid #eee;">
                        <p><strong>Message:</strong></p>
                        <p style="background: #f9f9f9; padding: 15px; border-radius: 5px;">{message}</p>
                        <br>
                        <p style="font-size: 12px; color: #777;">This message was sent via the sypheit.cloud contact form.</p>
                    </div>
                """
            }
        )

        # 6. Respond back to the browser
        status = "success" if res.status_code < 300 else "error"
        response_data = json.dumps({
            "status": status,
            "message": "Thank you for your message! We'll get back to you soon."
        })
        
        self.send_header('Content-Length', str(len(response_data)))
        self.end_headers()
        self.wfile.write(response_data.encode('utf-8'))