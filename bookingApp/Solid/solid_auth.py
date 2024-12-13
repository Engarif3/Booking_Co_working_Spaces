import requests
import logging

logger = logging.getLogger(__name__)

def solid_auth(idp, username, password):
    if not username or not password:
        raise ValueError("Username or password not provided")

    session = requests.Session()
    login_url = f"{idp}login/password"
    credentials = {"username": username, "password": password}
    response = session.post(login_url, data=credentials, allow_redirects=False)

    if response.status_code == 200 or response.status_code == 302:
        logger.info("Login attempt indicates success (or redirect).")
    else:
        logger.error(f"Failed to log in with status code {response.status_code} and response: {response.text}")
        session.close()
        raise Exception(f"User not logged in with status code {response.status_code}")

    return session



