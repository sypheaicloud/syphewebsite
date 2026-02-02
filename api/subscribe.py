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

        # --- 1. SEND WELCOME EMAIL TO SUBSCRIBER FROM YOUR DOMAIN ---
        requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Sypheit Newsletter <newsletter@sypheit.cloud>",
                "to": [subscriber_email],
                "subject": "Welcome to the Family! 🚀",
                "html": f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
                        <h2 style="color: #007bff;">Thanks for joining!</h2>
                        <p>Hi there,</p>
                        <p>We're thrilled to have you on board. You'll be the first to hear about our latest updates, tech insights, and news directly from <strong>sypheit.cloud</strong>.</p>
                        <div style="background: #f4f4f4; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
                            <p style="margin: 0;">Stay tuned for our next update!</p>
                        </div>
                        <p>Cheers,<br>The Sypheit Team</p>
                        <hr style="border: 0; border-top: 1px solid #eee; margin-top: 20px;">
                        <p style="font-size: 12px; color: #999; text-align: center;">
                            © 2026 sypheit.cloud. All rights reserved.
                        </p>
                    </div>
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
                "from": "System <admin@sypheit.cloud>",
                "to": ["sypheit@gmail.com"],
                "subject": "🔥 New Subscriber Alert!",
                "html": f"""
                    <div style="font-family: sans-serif;">
                        <p>Good news! You have a new subscriber:</p>
                        <p style="font-size: 18px; font-weight: bold; color: #28a745;">{subscriber_email}</p>
                    </div>
                """
            }
        )

        # 3. RESPOND TO THE BROWSER
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())