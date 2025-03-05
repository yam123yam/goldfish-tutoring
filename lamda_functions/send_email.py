import json
import boto3

# Initialize the SES client
ses_client = boto3.client('ses', region_name='us-east-1')  # Change region if needed

SENDER_EMAIL = "your_verified_email@example.com"  # Replace with your verified sender email

def lambda_handler(event, context):
    try:
        # Debugging: Print the received event
        print("Received event:", json.dumps(event, indent=2))

        recipient_email = event.get('recipient_email')
        subject = event.get('subject', 'Default Subject')
        message_body = event.get('message_body', 'Default Message')

        if not recipient_email:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Recipient email is required'})
            }

        # Send email
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': message_body}}
            }
        )

        print(f"Email sent to {recipient_email} with MessageId: {response['MessageId']}")
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Email sent successfully', 'SES_MessageId': response['MessageId']})
        }

    except Exception as e:
        print(f"Failed to send email to {recipient_email}. Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }