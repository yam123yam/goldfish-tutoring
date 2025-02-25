import hashlib
from boto3 import resource
from boto3.dynamodb.conditions import Key
from datetime import datetime

users_db = resource('dynamodb', region_name='us-east-2').Table('usersDB')

def lambda_handler(event, context):
    username = event['username']
    pet_name = event['pet_name']
    new_password = event['new_password']
    
    user_item = get_user_by_username(username)
    
    if user_item:
        stored_pet_name = user_item.get('pet_name')
        
        if stored_pet_name.lower() == pet_name.lower():
            if password_validity_check(new_password):
                hashed_new_password = hash_password(new_password)
                update_password_in_dynamo(username, hashed_new_password)
                return {"status": "success", "message": "Password updated successfully"}
            else:
                return {"status": "error", "message": "Invalid password format"}
        else:
            return {"status": "error", "message": "Incorrect pet name"}
    else:
        return {"status": "error", "message": "User not found"}

def get_user_by_username(username):
    response = users_db.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    return response['Items'][0] if response['Items'] else None

def update_password_in_dynamo(username, new_hashed_password):
    users_db.update_item(
        Key={'username': username},
        UpdateExpression='set #password=:s, updated_at=:n',
        ExpressionAttributeValues={
            ':s': new_hashed_password,
            ':n': datetime.now().isoformat()
        },
        ExpressionAttributeNames={'#password': 'password'},
        ReturnValues="UPDATED_NEW"
    )

def password_validity_check(password):
    return (len(password) >= 8 and
            any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in '$@#%^&*()_+!' for c in password))

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
