import json
import pytest
import boto3
import os
import sys
from unittest.mock import patch, MagicMock

# create a proper mock for xray_recorder that returns the original function 
class MockXRayRecorder:
    def capture(self, name):
        def decorator(func):
            return func # Return the original function without wrapping
        return decorator 
    
    def begin_subsegment(self, name):
        return MagicMock() 
    
    def end_subsegment(self): 
        pass  
    
    def current_subsegment(self):
        mock = MagicMock() 
        mock.add_exception = MagicMock() 
        return mock 
# Set up mocks before importing lambda_function 
mock_xray = MockXRayRecorder() 
sys.modules['aws_xray_sdk'] = MagicMock()  # Mock aws_xray_sdk for testing
sys.modules['aws_xray_sdk.core'] = MagicMock()  # Mock aws_xray_sdk.core for testing
sys.modules['aws_xray_sdk.core.xray_recorder'] = mock_xray  
sys.modules['aws_xray_sdk.core.patch_all'] = MagicMock() 
from lambda_function import lambda_handler

@pytest.fixture
def mock_env_variables():
    with patch.dict(os.environ, {
        'ALERTS_TABLE': 'mock-table',
        'SNS_TOPIC_ARN': 'mock-topic'
    }):
        yield

@pytest.fixture
def event_bridge_event():
    return {
        'source': 'demo.custom',
        'detail-type': 'Test Event',
        'detail': {'message': 'This is a test event'}
    }

@pytest.fixture
def mock_aws_services():
    with patch('lambda_function.dynamodb') as mock_dynamodb, \
         patch('lambda_function.sns') as mock_sns:
         # Setup mock table
         mock_table = MagicMock() 
         mock_dynamodb.Table.return_value = mock_table

         # Return all mocks 
         yield {
             'dynamodb' : mock_dynamodb,
             'table' : mock_table, 
             'sns' : mock_sns
         }

def test_lambda_handler_success(mock_env_variables, event_bridge_event, mock_aws_services):
    # Call the handler
    response = lambda_handler(event_bridge_event, {})
    
    # Verify response
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'alertId' in body
    
    # Verify DynamoDB was called
    mock_aws_services['table'].put_item.assert_called_once()
    
    # Verify SNS was called
    mock_aws_services['sns'].publish.assert_called_once()

def test_lambda_handler_exception(mock_env_variables, event_bridge_event, mock_aws_services):
    # Make DynamoDB throw an exception
    mock_aws_services['table'].put_item.side_effect = Exception("Test exception")
    
    # Call the handler
    response = lambda_handler(event_bridge_event, {})
    
    # Verify error response
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert 'error' in body
