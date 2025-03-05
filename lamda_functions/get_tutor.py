import json
import boto3
from boto3.dynamodb.conditions import Attr

# Initialize DynamoDB resources
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
users_db = dynamodb.Table('usersDB')

def lambda_handler(event, context):
    try:
        # Debugging: Print the received event
        print("Received event:", json.dumps(event, indent=2))

        # Extract the subject, date, and time from the event
        subject = event.get('subject')
        date = event.get('date')
        time = event.get('time')

        if not subject or not date or not time:
            return {"statusCode": 400, "body": json.dumps({"error": "All fields (subject, date, and time) are required"})}

        # Retrieve all tutors
        response = users_db.scan()
        tutors = response['Items']

        # Filter tutors based on subject
        subject_tutors = [tutor for tutor in tutors if any(s['M']['S']['S'].lower() == subject.lower() for s in tutor['subjects']['L'])]

        # Filter tutors based on availability
        available_tutors = []
        for tutor in subject_tutors:
            if 'availability' in tutor:
                for avail in tutor['availability']['L']:
                    avail_date = avail['M']['M']['M']['date']['M']['S']['S']
                    if avail_date == date:
                        for time_slot in avail['M']['M']['M']['times']['M']['L']:
                            start_time = time_slot['M']['M']['M']['start']['M']['S']['S']
                            end_time = time_slot['M']['M']['M']['end']['M']['S']['S']
                            if start_time <= time <= end_time:
                                available_tutors.append(tutor)
                                break

        # If no tutors found, return an error
        if not available_tutors:
            return {"statusCode": 404, "body": json.dumps({"error": "No available tutors found for the specified subject and time"})}

        # Return the list of available tutors
        return {"statusCode": 200, "body": json.dumps({"status": "success", "tutors": available_tutors})}

    except Exception as e:
        print("Error:", str(e))
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}