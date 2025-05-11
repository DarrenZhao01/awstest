import json
import boto3
import os
import base64
import sys
import uuid
from datetime import datetime

# Add the transcribe_utils module to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transcribe_utils.transcribe_audio import transcribe_audio_file

# Initialize AWS clients
s3_client = boto3.client('s3')

# S3 bucket configuration - will be set via environment variables in Lambda
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
S3_AUDIO_PREFIX = 'audio_responses/'

def lambda_handler(event, context):
    """
    AWS Lambda function to handle audio file uploads.
    This function is triggered by API Gateway and receives audio data.
    
    Using the Lambda Proxy integration with API Gateway.
    """
    try:
        # Get the content type
        content_type = event.get('headers', {}).get('content-type', '')
        
        # If this is a multipart form-data request
        if content_type and 'multipart/form-data' in content_type:
            # Extract boundary from content-type
            boundary = content_type.split('boundary=')[1].strip()
            
            # Parse the multipart form data
            body = event.get('body', '')
            if event.get('isBase64Encoded', False):
                body = base64.b64decode(body).decode('utf-8', errors='ignore')
                
            # Parse multipart form data
            form_data = parse_multipart_form(body, boundary)
            audio_content = form_data.get('audio', [''])[0]
            timestamp = form_data.get('timestamp', [datetime.now().isoformat()])[0]
            
            # Validate input
            if not audio_content:
                return create_response(400, {'error': 'No audio content found in the request'})
            
            # Generate a unique object name
            file_name = f"response_{timestamp.replace(':', '-').replace('.', '-')}.webm"
            s3_object_name = os.path.join(S3_AUDIO_PREFIX, file_name)
            
            # Upload the audio to S3
            if isinstance(audio_content, str):
                # If we received a string, it might be base64 encoded
                try:
                    audio_content = base64.b64decode(audio_content)
                except:
                    # If it's not base64, convert to bytes
                    audio_content = audio_content.encode('utf-8')
            
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_object_name,
                Body=audio_content,
                ContentType='audio/webm'
            )
            
            # Transcribe the audio file
            transcript = transcribe_audio_file(S3_BUCKET_NAME, s3_object_name)
            
            if transcript:
                return create_response(200, {
                    'message': 'Audio response uploaded and transcribed successfully.',
                    'filename': file_name,
                    's3_key': s3_object_name,
                    'transcript': transcript
                })
            else:
                return create_response(200, {
                    'message': 'Audio response uploaded but transcription failed.',
                    'filename': file_name,
                    's3_key': s3_object_name
                })
        else:
            return create_response(400, {'error': 'Invalid content type. Must be multipart/form-data.'})
    
    except Exception as e:
        print(f"Error processing audio upload: {str(e)}")
        return create_response(500, {'error': f"An error occurred: {str(e)}"})

def parse_multipart_form(body, boundary):
    """
    Parse multipart form data from the request body.
    This is a simplified parser and may need to be adjusted based on your specific needs.
    """
    # Convert to a more robust multipart parser in production
    form_data = {}
    parts = body.split(f'--{boundary}')
    
    for part in parts:
        if 'Content-Disposition: form-data' not in part:
            continue
        
        # Extract form field name
        if 'name="' not in part:
            continue
            
        field_name = part.split('name="')[1].split('"')[0]
        
        # Get the content after the double newline
        content = part.split('\r\n\r\n', 1)
        if len(content) > 1:
            value = content[1].strip()
            
            # If this is a file, handle binary data
            if 'filename="' in part:
                # For audio files, we need to handle binary data differently
                # This is simplified and might need adjustment
                content_type_line = part.split('\r\n')
                content_type = None
                for line in content_type_line:
                    if 'Content-Type:' in line:
                        content_type = line.split('Content-Type:')[1].strip()
                
                if content_type and 'audio/' in content_type:
                    # Handle binary audio data
                    # In a real implementation, you would need to properly extract the binary data
                    # without text encoding issues
                    pass
            
            # Store the form field value
            if field_name in form_data:
                form_data[field_name].append(value)
            else:
                form_data[field_name] = [value]
    
    return form_data

def create_response(status_code, body):
    """Create a standardized response for API Gateway."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # For CORS support
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        },
        'body': json.dumps(body)
    } 