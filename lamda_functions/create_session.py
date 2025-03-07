import json
import boto3
import uuid
from datetime import datetime
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resources
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
users_db = dynamodb.Table('usersDB')
session_db = dynamodb.Table('sessionDB')

# Initialize the SES client
ses_client = boto3.client('ses', region_name='us-east-1')  # Change region if needed

SENDER_EMAIL = "qbuchl001@stpaul.k12.mn.us"

def lambda_handler(event, context):
    try:
        # Debugging: Print the received event
        print("Received event:", json.dumps(event, indent=2))

        # Extract the tutor and student usernames from the event
        tutor_username = event.get('tutor_username')
        student_username = event.get('student_username')
        date = event.get('date')
        time = event.get('time')

        if not tutor_username or not student_username:
            return {"statusCode": 400, "body": json.dumps({"error": "Both tutor_username and student_username are required"})}

        # Retrieve tutor and student details from DynamoDB
        tutor = get_user_by_username(tutor_username)
        student = get_user_by_username(student_username)

        if not tutor or not student:
            return {"statusCode": 404, "body": json.dumps({"error": "Tutor or student not found"})}

        # Ensure the uuid key is present
        if 'user_id' not in tutor or 'user_id' not in student:
            return {"statusCode": 400, "body": json.dumps({"error": "user_id not found for tutor or student"})}

        # Generate session details
        session_id = create_session_UUID()
        
        created_at = get_time()
        updated_at = created_at

        # Store session details in DynamoDB
        session_db.put_item(
            Item={
                'session_UUID': session_id,
                'tutor_id': tutor['user_id'],
                'student_id': student['user_id'],
                'tutor_email': tutor['email'],
                'student_email': student['email'],
                'date': date,
                'time': time,
                'created_at': created_at,
                'updated_at': updated_at,
            }
        )

        # Send email to both tutor and student
        #send_email(tutor['email'], f"Session Created with {student['username']}", f"A session has been created with {student['username']} on {date} at {time}.")
        #send_email(student['email'], f"Session Created with {tutor['username']}", f"A session has been created with {tutor['username']} on {date} at {time}.")

        return {"statusCode": 200, "body": json.dumps({"status": "success", "message": "Session created successfully"})}

    except Exception as e:
        print("Error:", str(e))
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

def get_user_by_username(username):
    response = users_db.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    return response['Items'][0] if response['Items'] else None

def create_session_UUID():
    return str(uuid.uuid4())

def get_time():
    return datetime.now().isoformat()

def send_email(recipient_email, subject, message_body):
    try:
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': message_body}}
            }
        )
        print(f"Email sent to {recipient_email} with MessageId: {response['MessageId']}")
    except Exception as e:
        print(f"Failed to send email to {recipient_email}. Error: {str(e)}")