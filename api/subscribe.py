from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data)
        except:
            data = {}

        subscriber_email = data.get('email')
        api_key = os.environ.get("RESEND_API_KEY")

        if not subscriber_email:
            self.send_response(400)
            self.end_headers()
            return

        # --- 1. SEND WELCOME EMAIL TO SUBSCRIBER ---
        requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Newsletter <onboarding@resend.dev>",
                "to": [subscriber_email],
                "subject": "Welcome to our Newsletter! 🚀",
                "html": f"""
                    <h1>Thanks for joining!</h1>
                    <p>Hi there,</p>
                    <p>We're thrilled to have you on board. You'll be the first to hear about our latest updates and news.</p>
                    <br>
                    <p>Cheers,<br>The Team</p>
                """
            }
        )

        # --- 2. SEND NOTIFICATION TO YOU ---
        requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "System <onboarding@resend.dev>",
                "to": ["sypheit@gmail.com"],
                "subject": "New Subscriber Alert!",
                "html": f"<p>A new person just subscribed: <strong>{subscriber_email}</strong></p>"
            }
        )

        # 3. RESPOND TO THE BROWSER
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())