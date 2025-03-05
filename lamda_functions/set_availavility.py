#import dependencies
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
        username = event['username']['S']  # Extract the string value
        subjects = event['subjects']['L']  # Extract the list of subjects
        availability = event['availability']['L']  # Extract the list of availability
        if not username or not subjects or not availability:
            return {
                "status": "error",
                "message": "Missing required fields: username, subjects, or availability"
            }

        updated_at = get_time()

        # Update DynamoDB Item
        response = users_db.update_item(
            Key={"username": username},  # Use the extracted string value
            UpdateExpression='SET subjects = :s, availability = :a, updated_at = :u',
            ExpressionAttributeValues={
                ':s': subjects,
                ':a': availability,
                ':u': updated_at
            },
            ReturnValues="UPDATED_NEW"
        )
        #return response to the client
        return {"status": "success", "message": "Update successful"}

    # Error handling
    except KeyError as e:
        return {"status": "error", "message": f"Invalid input format: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

#helper function to get the current time
def get_time():
    return datetime.now().isoformat()

