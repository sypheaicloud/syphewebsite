from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from urllib.parse import parse_qs # Add this import at the top

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')

        # Check if data is JSON or Form-encoded
        content_type = self.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            data = json.loads(post_data)
        else:
            # This handles standard HTML form submissions
            parsed_data = parse_qs(post_data)
            data = {k: v[0] for k, v in parsed_data.items()}

        # Extract data
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject', 'No Subject')
        message = data.get('message')

        api_key = os.environ.get("RESEND_API_KEY")
        
        # Send via Resend
        res = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Website <onboarding@resend.dev>",
                "to": ["sypheit@gmail.com"],
                "subject": f"Contact Form: {subject}",
                "html": f"<h3>New Message</h3><p><strong>From:</strong> {name} ({email})</p><p><strong>Message:</strong> {message}</p>"
            }
        )

        self.send_response(200 if res.status_code < 300 else 500)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())