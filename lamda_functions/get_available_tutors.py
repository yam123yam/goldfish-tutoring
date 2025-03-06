import json
import boto3
from boto3.dynamodb.conditions import Attr
from datetime import datetime

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

        # Get day of week from the date
        request_date_obj = datetime.strptime(date, '%Y-%m-%d')
        day_of_week = request_date_obj.strftime('%A')  # Monday, Tuesday, etc.

        # Retrieve all tutors
        response = users_db.scan()
        tutors = response['Items']

        available_tutors = []
        for tutor in tutors:
            # Check if tutor teaches the requested subject
            tutor_subjects = []
            if 'subjects' in tutor:
                if isinstance(tutor['subjects'], list):
                    # Handle list of dictionaries format
                    tutor_subjects = [s.get('S', '').lower() for s in tutor['subjects'] if isinstance(s, dict) and 'S' in s]
                elif isinstance(tutor['subjects'], str):
                    tutor_subjects = [tutor['subjects'].lower()]
            
            # If subject matches, check availability
            if subject.lower() in tutor_subjects:
                # First, check date-based availability
                if 'availability' in tutor and isinstance(tutor['availability'], list):
                    for avail in tutor['availability']:
                        if isinstance(avail, dict) and 'M' in avail:
                            avail_dict = avail['M']
                            avail_date = avail_dict.get('date', {}).get('S', '')
                            
                            # Format dates consistently (remove leading zeros if necessary)
                            formatted_date = date.replace('-0', '-')
                            formatted_avail_date = avail_date.replace('-0', '-')
                            
                            if formatted_avail_date == formatted_date:
                                times = avail_dict.get('times', {}).get('L', [])
                                for t in times:
                                    if isinstance(t, dict) and 'M' in t:
                                        time_slot = t['M']
                                        start = time_slot.get('start', {}).get('S', '')
                                        end = time_slot.get('end', {}).get('S', '')
                                        if start <= time <= end:
                                            available_tutors.append({
                                                'username': tutor.get('username', ''),
                                                'email': tutor.get('email', ''),
                                                'subjects': tutor_subjects
                                            })
                                            break
                
                # Next, check day-of-week based availability
                elif 'availability' in tutor and isinstance(tutor['availability'], dict):
                    if day_of_week in tutor['availability']:
                        time_slots = tutor['availability'][day_of_week]
                        for slot in time_slots:
                            if isinstance(slot, str) and '-' in slot:
                                start_time, end_time = slot.split('-')
                                if start_time <= time <= end_time:
                                    available_tutors.append({
                                        'username': tutor.get('username', ''),
                                        'email': tutor.get('email', ''),
                                        'subjects': tutor_subjects
                                    })
                                    break

        # If no tutors found, return an error
        if not available_tutors:
            return {"statusCode": 404, "body": json.dumps({"error": "No available tutors found for the specified subject and time"})}

        # Return the list of available tutors
        return {"statusCode": 200, "body": json.dumps({"status": "success", "tutors": available_tutors})}

    except Exception as e:
        print("Error:", str(e))
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}