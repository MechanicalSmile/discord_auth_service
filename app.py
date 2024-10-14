"""
A Flask application that manages the OAuth login process with Discord 
and handles user data redirection to a specified backend application.

This application connects to a MongoDB database to retrieve associated 
redirect URLs for different applications, allowing users to authenticate 
via Discord and send their data to a specified endpoint. It uses 
environment variables for configuration, handles errors, and logs 
important events.

Dependencies:
- Flask: For creating the web application.
- python-dotenv: For loading environment variables from a .env file.
- pymongo: For interacting with MongoDB.
- requests: For making HTTP requests to the Discord API.
- werkzeug: For handling proxy fixes.

Environment Variables:
- DISCORD_CLIENT_ID: Client ID for the Discord application.
- DISCORD_CLIENT_SECRET: Client secret for the Discord application.
- DISCORD_REDIRECT_URI: Redirect URI registered with the Discord application.
- MONGO_URI: Connection string for the MongoDB database.

The application provides the following routes:
- /login: Initiates the login process by redirecting to Discord OAuth.
- /callback: Handles the callback from Discord after the user has 
  authorized the application.
"""
import logging
import requests
import os
import warnings
from dotenv import load_dotenv
from flask import Flask, redirect, request
from pymongo import MongoClient
from werkzeug.middleware.proxy_fix import ProxyFix


# Warn about SSL verification being disabled for HTTP requests
warnings.warn("SSL verification is disabled!", UserWarning)

# Configure logging to log to a file and to the console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)

# Initialize the Flask application
app = Flask(__name__)

# Load environment variables from the .env file
load_dotenv()

# Retrieve necessary environment variables for Discord and MongoDB
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI')
MONGO_URI = os.getenv('MONGO_URI')

# Check if essential environment variables are set
if not DISCORD_CLIENT_ID or not DISCORD_CLIENT_SECRET or not DISCORD_REDIRECT_URI or not MONGO_URI:
    raise ValueError("Missing essential environment variables.")

# Try to connect to the MongoDB database
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client['RedirectManager']  # Database for managing redirects
    discord_redirect_urls = db['discord_redirect_urls']  # Collection for redirect URLs
    logging.info("Connected to MongoDB successfully.")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {str(e)}")
    raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")

@app.route('/login')
def login():
    """Handles the login route, initiates OAuth flow with Discord."""
    logging.info(f"login route MONGO_URI: {MONGO_URI}")
    app_name = request.args.get('app')  # Get the application name from the request
    try:
        app_record = discord_redirect_urls.find_one({"app_name": app_name})  # Fetch app record from DB
    except Exception as e:
        logging.error(f"Error fetching app record from MongoDB: {str(e)}")
        return "Error fetching app record from the database.", 500  # Return error if DB fetch fails
    
    # If no associated URL found, return an error
    if app_record is None:
        logging.error(f"No associated URL found for the app '{app_name}'")
        return f"Error: No associated URL found for the app '{app_name}'", 400
    
    # Proceed to Discord OAuth if a user data post URL is found
    if app_record and "user_data_post_url" in app_record:
        logging.info(f"Found associated URL for the app: {app_name}, redirecting to Discord OAuth")
        scope = "identify email"  # Scopes for Discord OAuth
        state = app_name  # State parameter to maintain application context
        # Redirect to Discord authorization URL
        return redirect(f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope={scope}&state={state}")
    else:
        logging.error(f"No user data post URL found in app record for '{app_name}'")
        return f"Error: No associated URL found for the app '{app_name}'", 400

@app.route('/callback')
def callback():
    """Handles the callback from Discord after user authorization."""
    code = request.args.get('code')  # Get authorization code from the request
    app_name = request.args.get('state')  # Retrieve the app name from state parameter
    logging.info(f"Callback received for app: {app_name}, with code: {code}")

    # Request an access token from Discord using the authorization code
    try:
        token_response = requests.post("https://discord.com/api/oauth2/token", data={
            'client_id': DISCORD_CLIENT_ID,
            'client_secret': DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': DISCORD_REDIRECT_URI,
        }, timeout=10)
        
        # Check for successful token retrieval
        if token_response.status_code != 200:
            error_message = token_response.json().get('error_description', 'Unknown error')
            logging.error(f"Failed to retrieve access token for {app_name}. Error: {error_message}")
            return f"Error: Failed to retrieve access token. {error_message}", 400

        token_json = token_response.json()
        access_token = token_json.get('access_token')  # Extract access token
        if not access_token:
            logging.error("Access token not found in the response.")
            return "Error: Access token not found in the response.", 400

        logging.info(f"Successfully retrieved access token for {app_name}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Exception occurred during token request: {str(e)}")
        return "Error: Exception occurred during token request.", 500

    # Use the access token to retrieve user data from Discord
    try:
        user_response = requests.get("https://discord.com/api/users/@me", headers={
            'Authorization': f'Bearer {access_token}'
        }, timeout=10)
        
        if user_response.status_code != 200:
            error_message = user_response.json().get('error_description', 'Unknown error')
            logging.error(f"Failed to fetch user data from Discord for {app_name}. Error: {error_message}")
            return f"Error: Failed to fetch user data from Discord. {error_message}", 400
        
        user_data = user_response.json()  # Extract user data
        logging.info(f"Successfully retrieved user data for {app_name}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Exception occurred while fetching user data: {str(e)}")
        return "Error: Exception occurred while fetching user data.", 500
    
    # Fetch the app record again for the user data post URL
    app_record = discord_redirect_urls.find_one({"app_name": app_name})

    # Check if the record contains the user data post URL
    if app_record and "user_data_post_url" in app_record:
        backend_application_post_url = app_record["user_data_post_url"]
    else:
        logging.error(f"No associated URL found for the app '{app_name}' during callback.")
        return f"Error: No associated URL found for the app '{app_name}'", 400

    # Post the user data to the specified backend URL
    try:
        post_response = requests.post(backend_application_post_url, json={
            "app": app_name,
            "user": user_data
        }, verify=False)  # SSL verification is disabled (not recommended)

        # Check if posting user data was successful
        if post_response.status_code != 200:
            logging.error(f"Failed to send user data to backend. Response: {post_response.text}")
            return f"Error sending user data to backend: {post_response.text}", 400

        login_url = post_response.json().get("login_url")  # Extract login URL from response
        if not login_url:
            logging.error("No login URL received from backend.")
            return "Error: No login URL received from the backend.", 400

        logging.info(f"Redirecting user to login URL: {login_url}")
        return redirect(login_url)  # Redirect user to the login URL

    except requests.exceptions.RequestException as e:
        logging.error(f"Exception occurred while sending user data to backend: {str(e)}")
        return "Error: Exception occurred while sending user data to backend.", 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handles unhandled exceptions and logs them."""
    logging.error(f"Unhandled exception: {str(e)}")
    return "An error occurred. Please try again later.", 500

# Configure the application to work behind a reverse proxy (e.g., Nginx)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
