import json
from datetime import datetime
from boto3 import resource

# Initialize DynamoDB Table
users_db = resource('dynamodb', region_name='us-east-2').Table('usersDB')

def lambda_handler(event, context):
    try:
        # Debugging: Print the received event
        print("Received event:", json.dumps(event, indent=2))

        # Ensure required fields exist
        username = event['username']
        subjects = event['subjects']
        availability = event['availability']
        if not username or not subjects or not availability:
            return {
                "status": "error",
                "message": "Missing required fields: username, subject, or availability"
            }

        updated_at = get_time()

        # Update DynamoDB Item
        response = users_db.update_item(
            Key={"username": username},
            UpdateExpression='SET subjects = :s, availability = :a, updated_at = :u',
            ExpressionAttributeValues={
                ':s': subjects,
                ':a': availability,  # Ensure this is a valid JSON structure (list/dict)
                ':u': updated_at
            },
            ReturnValues="UPDATED_NEW"
        )

        print("Update successful:", response)
        return {"status": "success", "message": "Update successful"}

    except Exception as e:
        print("Error:", str(e))
        return {"status": "error", "message": str(e)}

def get_time():
    return datetime.now().isoformat()
