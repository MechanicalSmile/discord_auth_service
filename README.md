Discord OAuth Flask Application
A Flask application that manages the OAuth login process with Discord and handles user data redirection to a specified backend application. This application connects to a MongoDB database to retrieve associated redirect URLs for different applications, allowing users to authenticate via Discord and send their data to a specified endpoint. It utilizes environment variables for configuration, handles errors, and logs important events.

Table of Contents
Features
Dependencies
Environment Variables
Installation
Usage
Docker
Contributing
License
Features
OAuth authentication via Discord
MongoDB integration for managing redirect URLs
Error handling and logging for important events
SSL/TLS support for secure communications (with proper configuration)
Configurable via environment variables
Dependencies
This application requires the following Python packages:

Flask
python-dotenv
pymongo
requests
Werkzeug
Python Requirements
You can find the specific versions in the requirements.txt file:


```
blinker==1.8.2
certifi==2024.8.30
charset-normalizer==3.3.2
click==8.1.7
colorama==0.4.6
dnspython==2.6.1
Flask==3.0.3
gunicorn==23.0.0
idna==3.10
itsdangerous==2.2.0
Jinja2==3.1.4
MarkupSafe==2.1.5
packaging==24.1
pymongo==4.9.1
python-dotenv==1.0.1
requests==2.32.3
urllib3==2.2.3
Werkzeug==3.0.4
```
Environment Variables
Make sure to set the following environment variables in your .env file:

```
DISCORD_CLIENT_ID=<Your Discord Client ID>
DISCORD_CLIENT_SECRET=<Your Discord Client Secret>
DISCORD_REDIRECT_URI=<Your Discord Redirect URI>
MONGO_URI=<Your MongoDB Connection String>
```
Installation
Clone the repository:

```
git clone <repository-url>
cd <repository-directory>
```
Create a .env file in the root of the project and set the required environment variables.

Install dependencies:

```
pip install -r requirements.txt
```
Usage
To run the application locally, use the following command:

```
flask run
```
Visit http://localhost:5000/login?app=<your_app_name> to initiate the login process via Discord.

Docker
You can run this application using Docker. Follow these steps:

Build the Docker image:

```
docker-compose build
```
Run the Docker container:

```
docker-compose up
```
The application will be accessible at http://localhost:5000.

Docker Compose Configuration
The docker-compose.yml file is configured to use the .env file for environment variables and maps necessary certificate files for SSL/TLS support.

Contributing
Contributions are welcome! Please follow these steps:

Fork the repository.
Create a new branch (git checkout -b feature/YourFeature).
Make your changes and commit them (git commit -m 'Add new feature').
Push to the branch (git push origin feature/YourFeature).
Create a pull request.
License
This project is licensed under the MIT License. See the LICENSE file for details.

