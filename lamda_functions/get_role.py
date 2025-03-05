import json
import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
users_db = dynamodb.Table('usersDB')

def lambda_handler(event, context):
    username = event.get('username')  # Use .get() to avoid KeyError
    if not username:
        return {"error": "Username is required"}

    user_item = get_user_by_username(username)

    if user_item:
        return {"role": user_item.get('role')}
    else:
        return {"error": "User not found"}

def get_user_by_username(username):
    response = users_db.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    return response['Items'][0] if response['Items'] else None
#ignore