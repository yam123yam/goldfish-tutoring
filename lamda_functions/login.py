#import resources
import hashlib
from boto3 import resource
from boto3.dynamodb.conditions import Key

#initialize DynamoDB Table
users_db = resource('dynamodb', region_name='us-east-2').Table('usersDB')

#define the Lambda function, the event parameter is the input to the function
def lambda_handler(event, context):
    username = event['username']
    password = event['password']
    
    user_item = get_user_by_username(username)
    
    #if the username is found in the table, check if the password is correct
    if user_item:
        stored_hashed_password = user_item.get('password')
        input_hashed_password = hash_password(password)

    # check if the inputed password matches the stored password
        if input_hashed_password == stored_hashed_password:
            return {"status": "success", "message": "Login successful"}
        else:
            return {"status": "error", "message": "Incorrect password"}
    else:
        return {"status": "error", "message": "User not found"}

#check is the user exists in the table
def get_user_by_username(username):
    response = users_db.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    return response['Items'][0] if response['Items'] else None

#hash the password
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


