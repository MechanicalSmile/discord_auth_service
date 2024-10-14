# Discord OAuth Flask Application

A Flask application that manages the OAuth login process with Discord and handles user data redirection to a specified backend application. This application connects to a MongoDB database to retrieve associated redirect URLs for different applications, allowing users to authenticate via Discord and send their data to a specified endpoint. It utilizes environment variables for configuration, handles errors, and logs important events.
## Overview

This Flask application is designed to manage the OAuth login process with Discord and handle user data redirection to a specified backend application. It is specifically configured to run behind an Nginx server, which helps with load balancing and serves as a reverse proxy to manage client requests effectively.

## Reverse Proxy Configuration

The application is configured to operate behind Nginx. It uses `ProxyFix` to ensure that client requests are correctly processed and that the application retrieves the correct client IP addresses and protocols. Here are a few points to consider for your Nginx setup:

- Ensure that Nginx is configured to forward the appropriate headers (like `X-Forwarded-For`, `X-Forwarded-Proto`) to the Flask application.
- You can use the following configuration snippet in your Nginx server block to set up the reverse proxy:

    ```nginx
    server {
        listen 80;
        server_name yourdomain.com;

        location / {
            proxy_pass http://127.0.0.1:5000;  # Flask app running on localhost port 5000
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

Make sure to adjust the `server_name` and `proxy_pass` directives to match your setup.

## Security Considerations

**Important**: This application disables SSL verification for HTTP requests when posting user data to the backend. This poses a significant security risk. Ensure that SSL verification is enabled in production environments by setting `verify=True` in your HTTP requests.


## Table of Contents

- [Features](#features)
- [Dependencies](#dependencies)
- [Environment Variables](#environment-variables)
- [MongoDB Entry Format](#mongodb-entry-format)
- [Installation](#installation)
- [Usage](#usage)
- [Docker](#docker)
- [Contributing](#contributing)
- [License](#license)
- 
## Features

- OAuth authentication via Discord
- MongoDB integration for managing redirect URLs
- Error handling and logging for important events
- SSL/TLS support for secure communications (with proper configuration)
- Configurable via environment variables

## Dependencies
This application requires the following Python packages:

- Flask
- python-dotenv
- pymongo
- requests
- Werkzeug
### Python Requirements

You can find the specific versions in the `requirements.txt` file:
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

## Environment Variables

Make sure to set the following environment variables in your `.env` file:
```
DISCORD_CLIENT_ID=<Your Discord Client ID>
DISCORD_CLIENT_SECRET=<Your Discord Client Secret>
DISCORD_REDIRECT_URI=<Your Discord Redirect URI>
MONGO_URI=<Your MongoDB Connection String>
```
## MongoDB Entry Format
The MongoDB collection for managing redirects should contain entries in the following format:
```
{
    "app_name": "your_app_name",
    "redirect_url": "your_app_redirect_url",
    "user_data_post_url": "your_app_user_data_post_url"
}
```
- app_name: The name of your application.
- redirect_url: The URL to redirect users after successful login.
- user_data_post_url: The URL to post user data to your backend application.

## Installation

#### Clone the repository:
```
git clone <repository-url>
cd <repository-directory>
```
#### Create a `.env` file in the root of the project and set the required environment variables.

#### Install dependencies:
```
pip install -r requirements.txt
```

## Usage
To run the application locally, use the following command:
```
flask run
```
Visit `http://localhost:5000/login?app=<your_app_name>` to initiate the login process via Discord.

**Important:** When sending user data to the specified `backend_application_post_url`, ensure that your backend application responds with the login redirect URL. This URL should be included in the response of the POST request.
### Example of Login Redirect URL in Response
When the user data is successfully posted to the backend application, the backend should respond with a JSON object that includes the login redirect URL. For example:
```
{
    "login_url": "http://your-app.com/dashboard"
}
```
In this example, after successful authentication and data submission, users will be redirected to `http://your-app.com/dashboard`.

## Docker
You can run this application using Docker. Follow these steps:

#### Build the Docker image:
```
docker-compose build
```

#### Run the Docker container:
```
docker-compose up
```
The application will be accessible at `http://localhost:5000`.


### Docker Compose Configuration
The `docker-compose.yml` file is configured to use the `.env` file for environment variables and maps necessary certificate files for SSL/TLS support.

## Contributing
Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch `git checkout -b feature/YourFeature`.
3. Make your changes and commit them `git commit -m 'Add new feature'`.
4. Push to the branch `git push origin feature/YourFeature`.
5. Create a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

