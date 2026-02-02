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
                # Fallback for standard form submissions
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
                "html": f"""
                    <h3>New Message from Website</h3>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Subject:</strong> {subject}</p>
                    <hr>
                    <p><strong>Message:</strong></p>
                    <p>{message}</p>
                """
            }
        )

        # 6. Send response back to your website browser
        # We send 200 (Success) so your JavaScript 'alert' works
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # This JSON is what shows up in your browser console
        response_data = {
            "status": "success" if res.status_code < 300 else "error",
            "resend_code": res.status_code
        }
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

        # Log status to Vercel console for you to see
        print(f"Email sent! Resend Status: {res.status_code}, Response: {res.text}")