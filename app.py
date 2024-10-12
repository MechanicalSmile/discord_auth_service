from dotenv import load_dotenv
from flask import Flask, redirect, request
from pymongo import MongoClient
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
import os

# Load environment variables from a .env file (for storing secrets securely)
load_dotenv()
app = Flask(__name__)

# Retrieve Discord client ID, client secret, and redirect URI from environment variables
CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

MONGO_URI = "mongodb://localhost:27017"
# Establish connection to the MongoDB database
client = MongoClient(MONGO_URI)
db = client['DjangoProject']  # Replace with your database name
redirect_collection = db['redirect_urls']

@app.route('/login')
def login():
    """
    Handles the /login route.
    Redirects the user to the Discord OAuth2 authorization URL.
    """
    app_name = request.args.get('app')  # Capture the `app` parameter from the query string
    app_record = redirect_collection.find_one({"app_name": app_name})
    
    if app_record and "user_data_post_url" in app_record:
        scope = "identify email"  # The scope defines what permissions the app is requesting from the user
        state = app_name  # `state` is used to maintain state between the request and callback (usually for security purposes)
        return redirect(f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={scope}&state={state}")
    else:
        # If no matching app is found, handle the error gracefully
        return f"Error: No associated URL found for the app '{app_name}'", 400


@app.route('/callback')
def callback():
    """
    Handles the /callback route.
    This is the URL Discord will redirect to after the user authorizes the application.
    It will exchange the authorization code for an access token and retrieve user data.
    """
    code = request.args.get('code')  # Get the `code` parameter from the query string
    app_name = request.args.get('state')  # Get the `state` parameter to identify which app is making the request

    # Send a POST request to Discord to exchange the authorization code for an access token
    token_response = requests.post("https://discord.com/api/oauth2/token", data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,  
    })

    # Parse the response JSON to extract the access token
    token_json = token_response.json()
    access_token = token_json.get('access_token')

    # Use the access token to fetch user data from the Discord API
    user_response = requests.get("https://discord.com/api/users/@me", headers={
        'Authorization': f'Bearer {access_token}'
    })

    user_data = user_response.json()  # Extract user data from the response
    
    app_record = redirect_collection.find_one({"app_name": app_name})

    if app_record and "user_data_post_url" in app_record:
        django_backend_post_url = app_record["user_data_post_url"]
    else:
        return f"Error: No associated URL found for the app '{app_name}'", 400

    # Send the user data along with the `app_name` to a Django backend endpoint
    django_response = requests.post(django_backend_post_url, json={
        "app": app_name,  # Include the app name in the POST request to Django
        "user": user_data  # Include the retrieved Discord user data
    }, verify=False)

    if django_response.status_code != 200:
        return f"Error sending user data to Django backend: {django_response.text}", 400
    
     # Extract the login URL from the Django response
    login_url = django_response.json().get("login_url")

    if not login_url:
        return "Error: No login URL received from the Django backend.", 400

    # Redirect the user to the Django login URL
    return redirect(login_url)

if __name__ == '__main__':
    # Wrap the application with ProxyFix to handle headers when behind a proxy (like Nginx or a load balancer)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
    # Run the Flask application on localhost port 5000
    app.run(host='127.0.0.1', port=5000)
