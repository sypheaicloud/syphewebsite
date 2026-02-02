from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import parse_qs

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
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
        email = data.get('email', 'No Email')
        subject = data.get('subject', 'No Subject')
        message = data.get('message', 'No Message')

        # 4. Get API Key from Environment Variables
        api_key = os.environ.get("RESEND_API_KEY")
        
        # 5. Send the email via Resend
        # UPDATED: Using your custom domain sypheit.cloud
        res = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": f"{name} <hello@sypheit.cloud>",
                "to": ["sypheit@gmail.com"],
                "subject": f"Contact Form: {subject}",
                "reply_to": email, # This lets you click "Reply" in your email to talk to them
                "html": f"""
                    <div style="font-family: sans-serif; line-height: 1.5; color: #333;">
                        <h2 style="color: #007bff;">New Message from Sypheit.cloud</h2>
                        <p><strong>From:</strong> {name} ({email})</p>
                        <p><strong>Subject:</strong> {subject}</p>
                        <hr style="border: 0; border-top: 1px solid #eee;">
                        <p><strong>Message:</strong></p>
                        <p style="background: #f9f9f9; padding: 15px; border-left: 4px solid #007bff;">{message}</p>
                    </div>
                """
            }
        )

        # 6. Send response back to your website browser
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_data = {
            "status": "success" if res.status_code < 300 else "error",
            "resend_code": res.status_code
        }
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

        print(f"Email sent! Resend Status: {res.status_code}, Response: {res.text}")