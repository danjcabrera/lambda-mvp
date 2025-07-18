# Lambda event notification application -- Version 0.1 

## Components
1. Lambda Function (lambda_function.py)
- Processes events from EventBridge
- Logs to CloudWatch
- Uses X-Ray for tracing
- Saves alerts to DynamoDB
- Sends notifications via SNS
2. SAM Template (template.yaml)
- Defines the Lambda function
- Sets up DynamoDB table
- Creates SNS topic
- Configures EventBridge rules
- Sets up IAM permissions
3. Requirements (requirements.txt)
- boto3
- aws-xray-sdk

### Version Notes
Version 0.1
- Initial MVP implementation
- Event-driven architecture with EventBridge triggers
  - The function is triggered every 5 minutes by a scheduled event and can also be triggered by custom events with the source "demo.custom".
- CloudWatch logging
- X-Ray tracing
- DynamoDB for alert storage
- SNS for notifications
- No unit tests yet (planned for future versions)
- CI/CD with GitHub Actions (planned for future versions)
- Parameterizing the project for Organizational Sharing (planned for future versions)