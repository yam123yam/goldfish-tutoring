import hashlib
import uuid
from datetime import datetime
from boto3 import resource
from boto3.dynamodb.conditions import Key

users_db = resource('dynamodb', region_name='us-east-2').Table('usersDB')

def lambda_handler(event, context):
    username = event['username']
    password = event['password']
    email = event['email']
    phone_number = event['phone_number']
    pet_name = event['pet_name']
    role = event['role']
    full_name = event['full_name']
    grade = event['grade']

    if username_availability(username):
        return {"status": "error", "message": "Username already exists"}
    
    if password_validity_check(password):
        hashed_password = hash_password(password)
        UUID = create_UUID()
        created_at = updated_at = get_time()

        # Store user in DynamoDB
        response = users_db.put_item(
            Item={
                'username': username,
                'user_id': UUID,
                'password': hashed_password,
                'role': role,
                'full_name': full_name,
                'email': email,
                'phone_number': phone_number,
                'pet_name': pet_name,
                'grade': grade,
                'created_at': created_at,
                'updated_at': updated_at,
            }
        )
        return {"status": "success", "message": "Registration successful"}
    else:
        return {"status": "error", "message": "Invalid password format"}

def username_availability(username):
    response = users_db.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    return len(response['Items']) > 0

def password_validity_check(password):
    return (len(password) >= 8 and
            any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in '$@#%^&*()_+!' for c in password))

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_UUID():
    return str(uuid.uuid4())

def get_time():
    time = datetime.now().isoformat()
    return time