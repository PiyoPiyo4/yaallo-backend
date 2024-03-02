import json
import jwt
import re
import sqlite3
from datetime import datetime

regex = '^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$'

def generate_token(email, account_type):
    # NOTE: use id instead of email in the token!
    payload = {
        "email": email,
        "account_type": account_type, 
        "datetime": datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
    }
    return jwt.encode(payload, "", algorithm="HS256")