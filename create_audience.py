import requests, os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('RESEND_API_KEY')

res = requests.post(
    'https://api.resend.com/audiences',
    headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    },
    json={
        'name': 'Newsletter Subscribers'
    }
)

print(res.text)