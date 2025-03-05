import json
from datetime import datetime
from boto3 import resource

users_db = resource('dynamodb', region_name='us-east-2').Table('usersDB')

def lambda_handler(event, context):
    # Ensure keys exist before accessing them
    username = event.get("username")
    subject = event.get("subject")
    availability = event.get("availability")
    
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
            ':u': updated_at,
        },
        ExpressionAttributeNames={
            '#subjects': 'subjects'
        },
        ReturnValues="UPDATED_NEW"
    )
    print('Availability updated successfully')
    return {"status": "success", "message": "Availability updated successfully"}

def get_time():
    return datetime.now().isoformat()