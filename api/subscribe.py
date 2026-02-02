from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(post_data)

        email = data.get('email')
        api_key = os.environ.get("RESEND_API_KEY")

        # This adds the person to your Resend "Audience" list
        # Note: You need to create an "Audience" in the Resend dashboard first
        # and get the Audience ID, or just send an email to yourself instead:
        res = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Newsletter <onboarding@resend.dev>",
                "to": ["sypheit@gmail.com"],
                "subject": "New Newsletter Subscriber!",
                "html": f"<p>Add <strong>{email}</strong> to the mailing list.</p>"
            }
        )

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "subscribed"}).encode())