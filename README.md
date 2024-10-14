# Discord OAuth Flask Application

A Flask application that manages the OAuth login process with Discord and handles user data redirection to a specified backend application. This application connects to a MongoDB database to retrieve associated redirect URLs for different applications, allowing users to authenticate via Discord and send their data to a specified endpoint. It utilizes environment variables for configuration, handles errors, and logs important events.

## Table of Contents

- [Features](#features)
- [Dependencies](#dependencies)
- [Environment Variables](#environment-variables)
- [Installation](#installation)
- [Usage](#usage)
- [Docker](#docker)
- [Contributing](#contributing)
- [License](#license)

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

```plaintext
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
