import hashlib
import uuid
from datetime import datetime
from boto3 import resource
from boto3.dynamodb.conditions import Key

#initialize DynamoDB Table
users_db = resource('dynamodb', region_name='us-east-2').Table('usersDB')

#lambda function, add a new user to the table
def lambda_handler(event, context):
    #extract the required fields from the event
    username = event['username']
    password = event['password']
    email = event['email']
    phone_number = event['phone_number']
    pet_name = event['pet_name']
    role = event['role']
    full_name = event['full_name']
    grade = event['grade']

    #check if the username is already taken
    if username_availability(username):
        return {"status": "error", "message": "Username already exists"}
    
    #check if the password is valid
    if password_validity_check(password):
        hashed_password = hash_password(password)
        UUID = create_UUID()
        created_at = updated_at = get_time()
        subjects = []
        availability = []

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

                'subjects':subjects,
                'availability':availability,

                'created_at': created_at,
                'updated_at': updated_at,
            }
        )
        #return response to the client
        return {"status": "success", "message": "Registration successful"}
    else:
        return {"status": "error", "message": "Password must contain at least 1 Upper Case, Lower Case, a number, and a symbol"}

#check if the username is already taken
def username_availability(username):
    response = users_db.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    return len(response['Items']) > 0

#check if the password is valid
def password_validity_check(password):
    return (len(password) >= 8 and
            len(password) <= 30 and
            any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in '$@#%^&*()_+!' for c in password) )

#hash the password
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

#generate a UUID
def create_UUID():
    return str(uuid.uuid4())

#helper function to get the current time
def get_time():
    time = datetime.now().isoformat()
    return time



