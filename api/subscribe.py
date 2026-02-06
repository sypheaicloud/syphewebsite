from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Handle CORS for Vercel
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data)
        except:
            data = {}

        subscriber_email = data.get('email')
        api_key = os.environ.get("RESEND_API_KEY")

        if not subscriber_email:
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Email is required"}).encode())
            return

        try:
            # --- 1. SEND WELCOME EMAIL TO SUBSCRIBER ---
            welcome_res = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    # UPDATED: Using support@ for branding
                    "from": "Sypheit Newsletter <support@sypheit.cloud>",
                    "to": [subscriber_email],
                    "subject": "Welcome to the Family! 🚀",
                    "reply_to": "support@sypheit.cloud",
                    "html": f"""
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
                            <h2 style="color: #007bff;">Thanks for joining!</h2>
                            <p>Hi there,</p>
                            <p>We're thrilled to have you on board. You'll be the first to hear about our latest updates directly from <strong>sypheit.cloud</strong>.</p>
                            <hr style="border:none; border-top:1px solid #eee; margin: 20px 0;">
                            <p>Cheers,<br>The Sypheit Team</p>
                            <p style="font-size: 11px; color: #999;">You received this because you subscribed at sypheit.cloud</p>
                        </div>
                    """
                }
            )

            # --- 2. SEND NOTIFICATION TO ADMIN ---
            admin_res = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    # UPDATED: Using your internal admin identity
                    "from": "Sypheit System <support@sypheit.cloud>",
                    # UPDATED: Sending to support@ so it hits your professional flow
                    "to": ["support@sypheit.cloud"],
                    "subject": "🔥 New Subscriber Alert!",
                    "html": f"""
                        <div style="font-family: sans-serif; padding: 20px; background: #f4f4f4;">
                            <div style="background: white; padding: 20px; border-radius: 8px;">
                                <h3 style="margin-top: 0;">New Newsletter Subscriber</h3>
                                <p><strong>Email:</strong> {subscriber_email}</p>
                                <p style="font-size: 12px; color: #666;">View this contact in your Resend Audience dashboard.</p>
                            </div>
                        </div>
                    """
                }
            )

            # --- 3. ADD SUBSCRIBER TO AUDIENCE ---
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

            # --- 4. RESPOND TO BROWSER ---
            if welcome_res.status_code < 300:
                response_data = json.dumps({"status": "ok"})
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(response_data)))
                self.end_headers()
                self.wfile.write(response_data.encode())
            else:
                raise Exception(f"Resend API error: {welcome_res.text}")

        except Exception as e:
            print(f"Error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()