import json
from datetime import datetime
from boto3 import resource

users_db = resource('dynamodb', region_name='us-east-2').Table('usersDB')

def lambda_handler(event, context):
    # Ensure keys exist before accessing them
    username = event["username"]
    subject = event["subject"]
    availability = event["availability"]
    
    if not username or not subject or not availability:
        return {
            "status": "error",
            "message": "Missing required fields: username, subject, or availability"
        }

    updated_at = get_time()

    response = users_db.update_item(
        Key={
            'username': username,
        },
        UpdateExpression='set #subjects=:s, availability=:a, updated_at=:u',
        ExpressionAttributeValues={
            ':s': subject,
            ':a': availability,
            ':u': datetime.now().isoformat()
        },
        ExpressionAttributeNames={
            '#password': 'password'
        },
        ReturnValues="UPDATED_NEW"
    )
    print('Password updated successfully')
    return {"status": "success", "message": "Registration successful"}

def get_time():
    return datetime.now().isoformat()

