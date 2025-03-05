import json
import boto3
import uuid

# Initialize the Lambda client
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    try:
        # Debugging: Print the received event
        print("Received event:", json.dumps(event, indent=2))

        # Extract the user email from the event
        user_email = event.get('email')
        if not user_email:
            return {"statusCode": 400, "body": json.dumps({"error": "Email is required"})}

        # Generate a unique verification code
        verification_code = str(uuid.uuid4())

        # Prepare the payload for the send_email Lambda function
        payload = {
            "recipient_email": user_email,
            "subject": "Password Recovery Verification",
            "message_body": f"Your verification code is: {verification_code}"
        }

        # Invoke the send_email Lambda function
        response = lambda_client.invoke(
            FunctionName='arn:aws:lambda:us-east-2:123456789012:function:send_email',  # Replace with your send_email Lambda function ARN
            InvocationType='RequestResponse',  # Use 'Event' for asynchronous invocation
            Payload=json.dumps(payload)
        )

        # Parse the response from the send_email Lambda function
        response_payload = json.loads(response['Payload'].read())
        print("Response from send_email Lambda function:", response_payload)

        if response_payload.get('statusCode') == 200:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "success",
                    "message": "Verification email sent successfully"
                })
            }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "status": "error",
                    "message": "Failed to send verification email"
                })
            }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }