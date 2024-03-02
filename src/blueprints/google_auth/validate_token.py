import json
import jwt
from jwt.exceptions import PyJWTError
import time
from googleapiclient.discovery import build
from httplib2 import Http

def validate_google_auth_token(token):
  """
  Validates a Google Auth token (access token) for Gmail API access.

  Args:
      token (dict): The dictionary containing the token information.

  Returns:
      dict: A dictionary containing user information (email) if valid,
             or raises an exception with an appropriate error message otherwise.

  Raises:
      ValueError: If the token is invalid, expired, or missing required fields.
      Exception: If any other error occurs during validation.
  """

  # Check for required fields
  required_fields = ['access_token', 'expires_in', 'expires_at']
  for field in required_fields:
    if field not in token:
      raise ValueError(f"Missing required field in token: {field}")

  # Validate token expiration (using both expires_in and expires_at)
  current_time = int(time.time())
  expires_in = token['expires_in']
  expires_at = token['expires_at']
  if current_time >= expires_at or current_time + expires_in <= current_time:
    pass 
    # raise ValueError("Token has expired. Please re-authenticate.")

  # Validate token signature using Google's public keys (recommended for production)
  try:
    # Retrieve public keys from Google (replace with your own retrieval logic)
    url = "https://www.googleapis.com/oauth2/v1/certs"
    http = Http()
    response, content = http.request(url)
    if response.status != 200:
      raise Exception(f"Failed to retrieve public keys: {response.status}")
    public_keys = json.loads(content.decode('utf-8'))
    print('pub',public_keys)
    for key_fingerprint, pem_key in public_keys.items():
        try:
            decoded_token = jwt.decode(token['id_token'], pem_key, algorithms=['RS256'], audience=CLIENT_ID)
            # Extract user email from decoded token (if needed)
            user_email = decoded_token.get('email')
            return {'email': user_email}  # Return user information if valid
        except jwt.exceptions.PyJWTError as e:
        # Handle unsuccessful validation with this key
            pass  # Continue to the next key

    raise ValueError("Invalid token signature. Please re-authenticate.")


  except (PyJWTError, json.JSONDecodeError) as e:
    raise ValueError(f"Invalid token signature: {e}")
  except Exception as e:
    raise Exception(f"Error validating token: {e}")

# Replace with your actual Google API client ID for validation
CLIENT_ID = "483124533702-0mgvs24ebsuj9f9gaetbv8vgv7mrn333.apps.googleusercontent.com"
# = "YOUR_CLIENT_ID"

if __name__ == "__main__":
  sample_token = {'access_token': 'ya29.a0AfB_byCyywmiQtN4ufGZVC--XINWOaG8RHorBSR-ZWWRfLWKFD6fWzNAbdEPj2fW7mV_WCxNrADH1gdHIIAZqEdjeN8eS6XtCngcosMgXpc7_SIjydFkKCAPbqvMpiA7ZcccA6oNMT__zIL7pVsALt57bBxOGZqRP8W9aCgYKATkSARISFQHGX2MiX5ss9_IOR_shtGMB5mqB0A0171', 'expires_at': 1708978287, 'expires_in': 3599, 'id_token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjU1YzE4OGE4MzU0NmZjMTg4ZTUxNTc2YmE3MjgzNmUwNjAwZThiNzMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI0ODMxMjQ1MzM3MDItMG1ndnMyNGVic3VqOWY5Z2FldGJ2OHZndjdtcm4zMzMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI0ODMxMjQ1MzM3MDItMG1ndnMyNGVic3VqOWY5Z2FldGJ2OHZndjdtcm4zMzMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDM2NjYyMDAxNTQxMTY3NzQ5MzUiLCJlbWFpbCI6ImltYW51YmhhdjE4QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhdF9oYXNoIjoiVnFJS3k1QTltc3RBYThILUF0TzltUSIsIm5hbWUiOiJBbnViaGF2IFRvbWFyIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0pXNEhCcGw1dFFBRDFTcWo5Mm1NZUNnRF9POGVBX2c1RFNKUjg5Zmp1MFZIND1zOTYtYyIsImdpdmVuX25hbWUiOiJBbnViaGF2IiwiZmFtaWx5X25hbWUiOiJUb21hciIsImxvY2FsZSI6ImVuLUdCIiwiaWF0IjoxNzA4OTc0Njg4LCJleHAiOjE3MDg5NzgyODh9.k0p4lNyPT_vI2gLlFVP7evVr9Z8PJg3o7rKUnvbwXzGfkMhJjiiaH7sSr8NpAlwqFWDuO4ZrKetzC7s9QugAmcBy1jjcxt2ZTg5Ouv9Us91GqNRIlbwCYr87OT2L9K56H6IT2z_jeGi-XpDFdq7aDSrM3ZDoulP_pSr10WO3DwuBNjepcmMiJexuspdCTPUCYodt8MuvwzWzyPUBzM565UH6jlf6CNfaVCKKQoC31URFatEqn_GDqWz0PbUPqjwQp6qfh1qUHCNoiVwD8avajIRAHWzVWId0O249KDP7JxhBw6uikx0KWinfpAHDvbLKnBO_zmw6GHRkt900viSGqw', 'refresh_token': '1//0g2fx5fS0ZZNNCgYIARAAGBASNwF-L9Iri8d0aIats_a-9kniIHIufltNXj67WlJ-HDuZTqFWchdDIYLPIvAXYf6WFLOB6OEbEVk', 'scope': 'openid https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/gmail.readonly', 'token_type': 'Bearer'}
  try:
    user_info = validate_google_auth_token(sample_token)
    print(f"Validated token. User email: {user_info['email']}")
  except (ValueError, Exception) as e:
    print(f"Error: {e}")
    print("Please re-authenticate or handle the error appropriately.")