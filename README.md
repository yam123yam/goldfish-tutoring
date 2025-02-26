# goldfish-tutoring

this repo contains the lambda functions used to connect to AWS. 

To set up AWS: 
1. Create an Account
2. Open the AWS Console and go to IAM (Identity Access Management) and create a new lambda role that has permissions for DynamoDB and SES (simple email service) 
3. Open the AWS Console and go to Lambda
4. Create a new function, name it accodingly and paste this code
5. Create a test event with the required events
6. Open the AWS Consol and go to API Gateway
7. Here, create a new API with REST endpoints
8. Create a new path and then create a new method
9. choose Lambda funciton (POST)
10. Then copy the invoke URL and edit the frontend scripts.js file with the correct API endpoints 
