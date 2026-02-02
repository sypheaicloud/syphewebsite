from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        # Extract data from the JSON sent by JavaScript
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')

        api_key = os.environ.get("RESEND_API_KEY")
        
        # This sends the email using Resend
        res = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Website <onboarding@resend.dev>",
                "to": ["YOUR_REAL_EMAIL@GMAIL.COM"], # Replace with your email!
                "subject": f"New Contact: {subject}",
                "html": f"<p><strong>From:</strong> {name} ({email})</p><p><strong>Message:</strong> {message}</p>"
            }
        )

        self.send_response(200 if res.status_code < 300 else 500)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success"}).encode())