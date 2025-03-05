import json
import boto3
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def time_to_minutes(time_str):
    """Convert time string HH:MM to minutes since midnight."""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def format_date(date_str):
    """Normalize date format to handle different formats."""
    try:
        # Parse the date string into a datetime object
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return date_str

def extract_subjects(subjects_data):
    """Extract subjects from various data formats."""
    subjects = []
    
    if isinstance(subjects_data, list):
        for item in subjects_data:
            if isinstance(item, str):
                subjects.append(item.lower())
            elif isinstance(item, dict) and 'S' in item:
                subjects.append(item['S'].lower())
    elif isinstance(subjects_data, str):
        subjects.append(subjects_data.lower())
    elif isinstance(subjects_data, dict) and 'L' in subjects_data:
        for item in subjects_data['L']:
            if 'S' in item:
                subjects.append(item['S'].lower())
    
    return subjects

def check_availability(availability_data, requested_date, requested_time_minutes):
    """Check if the tutor is available at the requested date and time."""
    if not availability_data:
        return False
    
    normalized_requested_date = format_date(requested_date)
    
    try:
        if isinstance(availability_data, dict):
            for day, time_slots in availability_data.items():
                try:
                    date_obj = datetime.strptime(requested_date, "%Y-%m-%d")
                    weekday = date_obj.strftime("%A")
                    if day.lower() == weekday.lower():
                        for slot in time_slots:
                            start_time, end_time = map(time_to_minutes, slot.split('-'))
                            if start_time <= requested_time_minutes <= end_time:
                                return True
                except:
                    pass
        
        elif isinstance(availability_data, list):
            for avail in availability_data:
                avail_info = avail.get('M', {})
                avail_date = avail_info.get('date', {}).get('S')
                times_list = avail_info.get('times', {}).get('L', [])
                
                if avail_date and format_date(avail_date) == normalized_requested_date:
                    for time_slot in times_list:
                        time_data = time_slot.get('M', {})
                        start_time = time_to_minutes(time_data.get('start', {}).get('S', ''))
                        end_time = time_to_minutes(time_data.get('end', {}).get('S', ''))
                        if start_time <= requested_time_minutes <= end_time:
                            return True
    
    except Exception as e:
        logger.error(f"Error checking availability: {str(e)}")
    
    return False

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('usersDB')
    response = table.scan()
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    requested_subject = event['subject']
    requested_date = event['date']
    requested_time = event['time']

    requested_time_minutes = time_to_minutes(requested_time)

    available_tutors = []

    for tutor_data in data:
        subjects = extract_subjects(tutor_data.get('subjects', []))
        
        if requested_subject.lower() in subjects and check_availability(tutor_data.get('availability', []), requested_date, requested_time_minutes):
            
            available_tutors.append(tutor)
            
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "success",available_tutors})
            }

    return {
        "statusCode": 404,
        "body": json.dumps({"error": "No available tutors found for the specified subject and time"})
    }