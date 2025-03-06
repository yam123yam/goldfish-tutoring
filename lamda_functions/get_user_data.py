import json
import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
users_db = dynamodb.Table('usersDB')

def lambda_handler(event, context):
    try:
        # Extract the username from the event
        username = event.get('username')
        
        if not username:
            return {"statusCode": 400, "body": json.dumps({"error": "Username is required"})}
        
        # Fetch user data from DynamoDB
        response = users_db.get_item(Key={'username': username})
        
        if 'Item' not in response:
            return {"statusCode": 404, "body": json.dumps({"error": "User not found"})}
        
        user_data = response['Item']
        
        return {"statusCode": 200, "body": json.dumps(user_data)}
    
    except Exception as e:
        print("Error:", str(e))
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}