import hashlib
from boto3 import resource
from boto3.dynamodb.conditions import Key

users_db = resource('dynamodb', region_name='us-east-2').Table('usersDB')

def lambda_handler(event, context):
    username = event['username']
    password = event['password']
    
    user_item = get_user_by_username(username)
    
    if user_item:
        stored_hashed_password = user_item.get('password')
        input_hashed_password = hash_password(password)

        if input_hashed_password == stored_hashed_password:
            return {"status": "success", "message": "Login successful"}
        else:
            return {"status": "error", "message": "Incorrect password"}
    else:
        return {"status": "error", "message": "User not found"}

def get_user_by_username(username):
    response = users_db.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    return response['Items'][0] if response['Items'] else None

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
