from flask import Flask, redirect, request
from dotenv import load_dotenv
import requests
import os

load_dotenv()
app = Flask(__name__)

# Environment variables for your Discord app credentials
CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')  # Should exactly match what's in Discord Developer Portal

@app.route('/login')
def login():
    app_name = request.args.get('app')  # Get the app identifier from the query parameter
    scope = "identify email"  # Define the permissions you're requesting
    state = app_name  # Pass app_name through the state parameter

    # Generate the Discord authorization URL
    return redirect(f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={scope}&state={state}")

@app.route('/callback')
def callback():
    code = request.args.get('code')  # Retrieve the authorization code
    app_name = request.args.get('state')  # Retrieve the app_name from the state parameter

    # Exchange the authorization code for an access token
    token_response = requests.post("https://discord.com/api/oauth2/token", data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,  # Must match the exact URI set in the Discord Developer Portal
    })

    token_json = token_response.json()
    access_token = token_json.get('access_token')

    # Use the access token to fetch user data
    user_response = requests.get("https://discord.com/api/users/@me", headers={
        'Authorization': f'Bearer {access_token}'
    })

    user_data = user_response.json()  # User data includes ID, username, email, etc.

    django_backend_url = 'http://localhost:8000/your-django-endpoint/'
    requests.post(django_backend_url, json={
        "app": app_name,  # Pass the app name
        "user": user_data
    })
    # Return user data along with the app_name
    return redirect('http://localhost:8000')

if __name__ == '__main__':
    app.run(port=5000, ssl_context=('cert.pem', 'key.pem'), debug=True)
