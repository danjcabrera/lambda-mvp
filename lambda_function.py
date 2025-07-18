import json
import boto3
import os
import logging
import uuid
from datetime import datetime
import traceback
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Initialize X-Ray
patch_all()

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize clients
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

@xray_recorder.capture('lambda_handler')
def lambda_handler(event, context):
    """
    Lambda function that processses a trigger event, logs to CloudWatch,
    saves to DynamoDB, and sends an SNS notification.
    """ 

    # Get environment variables
    table_name = os.environ.get('ALERTS_TABLE', 'default-table')
    topic_arn = os.environ.get('SNS_TOPIC_ARN', 'default-topic')

    logger.info(f"Received event: {json.dumps(event)}")
      
    try:
        # Generate alert ID
        alert_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Extract source information from the event
        source = event.get('source', 'unknown')
        detail_type = event.get('detail-type', 'unknown')
        
        # Create alert item for DynamoDB
        alert_item = {
            'alertId': alert_id,
            'timestamp': timestamp,
            'source': source,
            'detailType': detail_type,
            'detail': json.dumps(event.get('detail', {})),
            'status': 'NEW'
        }
        
        # Add subsegment for DynamoDB operation
        subsegment = xray_recorder.begin_subsegment('save_to_dynamodb')
        try:
            # Save to DynamoDB
            table = dynamodb.Table(table_name)
            table.put_item(Item=alert_item)
            logger.info(f"Alert saved to DynamoDB with ID: {alert_id}")
        finally:
            xray_recorder.end_subsegment()
        
        # Add subsegment for SNS operation
        subsegment = xray_recorder.begin_subsegment('send_notification')
        try:
            # Send SNS notification
            message = f"New alert detected from {source}: {detail_type}"
            sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps({
                    'default': json.dumps(alert_item),
                    'email': message,
                    'sms': message
                }),
                MessageStructure='json',
                Subject=f"Alert: {detail_type}"
            )
            logger.info(f"Notification sent to SNS topic: {topic_arn}")
        finally:
            xray_recorder.end_subsegment()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Alert processed successfully',
                'alertId': alert_id
            })
        }
    
    except Exception as e:
        logger.error(f"Error processing alert: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Record error in X-Ray
        xray_recorder.current_subsegment().add_exception(
            exception=e,
            stack=traceback.extract_stack(),
            remote=False
        )
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
