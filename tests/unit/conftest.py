import pytest
import boto3
import os
from unittest.mock import patch, MagicMock
import moto

# Global test configuration
def pytest_configure(config):
    """Set up global test configuration"""
    # Disable AWS credentials for tests
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'  # Set your default region

# Shared fixtures that can be used across multiple test files
@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
@pytest.fixture(scope="function")
def dynamodb_mock(aws_credentials):
    """DynamoDB mock using moto"""
    with moto.mock_dynamodb():
        # Create the DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='mock-table',
            KeySchema=[{'AttributeName': 'alertId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'alertId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        yield table

@pytest.fixture(scope="function")
def sns_mock(aws_credentials):
    """SNS mock using moto"""
    with moto.mock_sns():
        # Create the SNS topic
        sns = boto3.client('sns', region_name='us-east-1')
        topic = sns.create_topic(Name='mock-topic')
        yield sns, topic['TopicArn']
