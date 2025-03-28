import http.client
import json
import socket
import requests
import uuid
import pyotp
import time

import os
from dotenv import load_dotenv
from SmartApi import SmartConnect
TOKEN_REFRESH_LIMIT = 3

load_dotenv()

API_KEY = os.getenv("SMARTAPI_KEY")
CLIENT_ID = os.getenv("SMARTAPI_CLIENT")
PASSWORD = os.getenv("SMARTAPI_PASS")
TOKEN = os.getenv("SMARTAPI_TOTP")
TOTP = pyotp.TOTP(TOKEN).now()

def load_session():
    """ Load session token from file. """
    try:
        with open("SESSION_FILE", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None

def save_session(data):
    """ Save session token to file. """
    with open("SESSION_FILE", "w") as file:
        json.dump(data, file)

def get_smartapi():
    """ Fetch session or re-login if necessary. """
    session_data = load_session()
    smartApi = SmartConnect(api_key=API_KEY)

    if session_data:
        auth_token = session_data.get("authToken")
        refresh_token = session_data.get("refreshToken")

        if auth_token:
            smartApi.setAccessToken(auth_token)
            # ✅ Test if the token is still valid before using it
            ltp_response = smartApi.ltpData("NSE", "RELIANCE", "2885")
            if ltp_response.get("status"):
                print("✅ Using Existing Token")
                return smartApi  # Return valid session
            
            print("⚠️ Token Expired! Refreshing Token...")
            return refresh_token_if_needed(smartApi, refresh_token)

    return login()  # If session is invalid, log in again

def refresh_token_if_needed(smartApi, refresh_token, retries=0):
    """ Refresh token if expired, with rate limit protection. """
    if retries >= TOKEN_REFRESH_LIMIT:
        print("❌ Too many token refresh attempts, logging in again.")
        return login()

    try:
        refresh_response = smartApi.generateToken(refresh_token)  # Double-check API docs

        if refresh_response.get("status"):
            new_token = refresh_response["data"]["jwtToken"]
            save_session({"authToken": new_token, "refreshToken": refresh_token})
            print("✅ Token Refreshed Successfully!")
            smartApi.setAccessToken(new_token)
            return smartApi
        else:
            print("❌ Refresh Token Invalid, Logging In Again...")
            return login()
    except Exception as e:
        print(f"⚠️ Token Refresh Failed: {str(e)} - Retrying...")
        time.sleep(2)  # Small delay before retry
        return refresh_token_if_needed(smartApi, refresh_token, retries + 1)

def login():
    """ Logs in and stores session token with rate limit protection. """
    print("🟢 Attempting Login...")
    time.sleep(3)  # Prevent excessive login attempts
    
    smartApi = SmartConnect(api_key=API_KEY)
    response = smartApi.generateSession(CLIENT_ID, PASSWORD, TOTP)

    if response.get("status"):
        print("✅ Login Successful!")
        session_data = {
            "authToken": response["data"]["jwtToken"],
            "refreshToken": response["data"]["refreshToken"]
        }
        save_session(session_data)
        return smartApi
    else:
        print("❌ Login Failed:", response)
        return None
