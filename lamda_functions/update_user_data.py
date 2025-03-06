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
    email = event['email']
    phone_number = event['phone_number']
    full_name = event['full_name']
    grade = event['grade']
    updated_at = get_time()

   
    response = users_db.update_item(
        Key={"username": username},  # Use the extracted string value
        UpdateExpression='SET email:e, full_name: f, phone_number = :n,updated_at = :u',
        ExpressionAttributeValues={
            'e':email, 
            'f':full_name,
            'n': phone_number,
            'u':updated_at        
        },
        ReturnValues="UPDATED_NEW"
    )
    #return response to the client
    return {"status": "success", "message": "Update successful"}

def get_time():
    time = datetime.now().isoformat()
    return time



