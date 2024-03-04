from hashlib import md5
from json import dumps
from flask import Flask, request, jsonify
from pymongo import MongoClient
import bcrypt
from functools import wraps
from flask_cors import CORS, cross_origin
import datetime

from token_config import *
from reset_password import *
import bson

# Replace with your actual MongoDB connection details
MONGO_URI = "mongodb+srv://dev:otUvobpvZlBBlNKm@cluster0.xumgfs7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


# def defaultHandler(err):
#     response = err.get_response()
#     print(response)
#     print('response', err, err.get_response())
#     response.data = dumps({
#         "code": err.code,
#         "name": "System Error",
#         "message": err.get_description(),
#     })
#     response.content_type = 'application/json'
#     return response
# ALLOWED_ORIGIN = "https://deluxe-liger-3e64ee.netlify.app/" 
app = Flask(__name__)
# cors = CORS(app, resources={"/": {"origins": [ALLOWED_ORIGIN]}})

@app.route('/')
def conn():
    print('HELLOW!')
    return 'WORKING PROPERLY'
#### LOGIN AND SIGN UP ####

@app.route('/login', methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def login():
    client = MongoClient(MONGO_URI)
    db = client["yaallo"]
    collection = db["users"]
    req = request.get_json()
    try:
        # Extract username/email and password from request body
        email = req['email']
        password = req['password']
    except KeyError:
        return jsonify({ 'status': 400,
                "body": {"message": "Missing required fields in request body"}})

    # Find user by email
    found_user = collection.find_one({"$or": [
        {"email": email}
    ]})
    if not found_user:
        return { 'status': 401,
                "body": {"message": "Invalid username/email or password"}}

    # Secure password comparison
    stored_password = found_user["password"].encode('utf-8')
    print(stored_password)
    if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
        return { 'status': 401,
                "body": {"message": "Invalid username/email or password"}}

    # Successful login
    token = generate_token(email, found_user['type'])
    return jsonify({ 'token': token, 'acc_type': found_user['type']})

@app.route('/brand-signup', methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def brandregister() :
    client = MongoClient(MONGO_URI)
    db = client["yaallo"]
    collection = db["users"]
    req = request.get_json()
    try:
        brandName = req['name']
        email = req['email']
        password = req['password']
        createdAt = datetime.now()
        updatedAt = datetime.now()
        type = req['type']
    except KeyError:
        return jsonify({ 'status': 400,
                "body": {"message": "Missing required fields in request body"}})
    salt = bcrypt.gensalt(10)
    bytespass = password.encode('utf-8')
    hashPass = str(bcrypt.hashpw(bytespass, salt))
    new = {'type': type,
           'brandName': brandName,
           'email': email,
           'password': hashPass[2:-1],
           'createdAt': createdAt,
           'updatedAt': updatedAt}
    # print(new)
    collection.insert_one(new)
    token = generate_token(email, new['type'])
    return jsonify({ 'token': token, 'acc_type': type})
    # return '1'

@app.route('/user-signup', methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def userregister() :
    client = MongoClient(MONGO_URI)
    db = client["yaallo"]
    collection = db["users"]
    req = request.get_json()
    try:
        firstName = req['firstName']
        lastName = req['lastName']
        email = req['email']
        password = req['password']
        createdAt = datetime.now()
        updatedAt = datetime.now()
        type = req['type']

    except KeyError:
        return jsonify({ 'status': 400,
                "body": {"message": "Missing required fields in request body"}})
    salt = bcrypt.gensalt(10)
    bytespass = password.encode('utf-8')
    hashPass = str(bcrypt.hashpw(bytespass, salt))
    new = {'type': type,
           'firstName': firstName,
           'lastName': lastName,
           'email': email,
           'password': hashPass[2:-1],
           'createdAt': createdAt,
           'updatedAt': updatedAt}
    # print(new)
    collection.insert_one(new)
    token = generate_token(email, new['type'])
    return jsonify({ 'token': token, 'acc_type': type})
    # return '1'

@app.route("/forgot-password", methods=["POST"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def forgot_password():
    client = MongoClient(MONGO_URI)
    db = client["yaallo"]
    collection = db["users"]
    req = request.get_json()
    email = req['email']
    
    if not email:
        return jsonify({"error": "Missing email address"}), 400


    # Find user by email
    user = collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "Email address not found"}), 404

    # Generate OTP
    otp = generate_otp()

    # Store OTP in user object (replace with secure storage)
    user["otp"] = otp
    collection.update_one({"_id": user["_id"]}, {"$set": user})

    # Send email with OTP
    subject = "Password Reset for Your Account"
    content = f"Your OTP for password reset is: {otp}"
    send_email(email, subject, content)

    return jsonify({"message": "OTP sent to your email address"})

@app.route("/otp-verify", methods=["POST"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def otp_verify():
    client = MongoClient(MONGO_URI)
    db = client["yaallo"]
    collection = db["users"]
    req = request.get_json()
    print(req)
    email = req["email"]
    otp = req["otp"]

    # Find user by email
    user = collection.find_one({"email": email})
    if user["otp"] == otp:
    # OTP matches and user is authenticated (handle successful authentication)
        print("OTP verified successfully!")
    else:
        # OTP does not match (handle invalid OTP)
        print("Invalid OTP!")
    return jsonify({"message": "OTP match verified"})

@app.route("/reset-password", methods=["POST"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def reset_password():
    client = MongoClient(MONGO_URI)
    db = client["yaallo"]
    collection = db["users"]
    req = request.get_json()
    email = req["email"]
    newpass = req["newPassword"]
    
    salt = bcrypt.gensalt(10)
    bytespass = newpass.encode('utf-8')
    hashPass = str(bcrypt.hashpw(bytespass, salt))

    # Find user by email
    user = collection.find_one({"email": email})
    user["password"] = hashPass[2:-1]
    collection.update_one({"_id": user["_id"]}, {"$set": user})

    return jsonify({"message": "Password Reset Success", 'status_code': 200})

#### GET POSTS ####
@app.route("/posts", methods=["POST"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def get_posts() :
    # return '23'
    client = MongoClient(MONGO_URI)
    db = client["yaallO"]
    collection_posts = db["posts"]

    # data = collection.find()
    req = request.get_json()
    page_size = req["pageSize"]  # Default page size
    page_number = req["pageNumber"] # Default page number
    print(page_number)
        # Skip documents based on page number and page size
    skip = (page_number - 1) * page_size

    # Retrieve documents with pagination
    cursor = collection_posts.find({}, {"_id": 0}, skip=skip, limit=page_size).sort("when", -1)

        # Convert cursor objects to a list of dictionaries
    posts = [post for post in cursor]
    # posts = []
    # for post in cursor:
    #     brid = post["brid"]
    #     # Find brand document in the other database
    #     brand_doc = collection_channel.find_one({"channel": brid} , {"_id": 0}) 
    #     # brand_id = brand_doc["_id"] if brand_doc else None

    #     post["brname"] = brand_doc['brname'] if brand_doc else "" 
    #     post['pp'] = brand_doc['pp'] if brand_doc else "" 
    #     post['fname'] = brand_doc['fname'] if brand_doc else "" 
    #     posts.append(post)

        # Return serialized data (e.g., JSON)
    
    # return posts  # Return status code 200 (OK)
    return jsonify(posts)


@app.route("/add", methods=["POST"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def add_data():
    client = MongoClient(MONGO_URI)
    db = client["yaallO"]
    collection = db["posts"]
    
    collection.update_many({}, {"$set": {"likes": random.randint(0, 25)}})
    
    return jsonify("SUCCESS")

    # return data
if __name__ == '__main__':
    app.run(debug=True)
