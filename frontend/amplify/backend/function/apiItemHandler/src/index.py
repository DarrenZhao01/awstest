import json
import os
import base64
import sys
from urllib.parse import parse_qs

# Mock S3 client for local testing
class MockS3Client:
    def __init__(self):
        self.storage = {}
    
    def put_object(self, Bucket, Key, Body, ContentType=None):
        if Bucket not in self.storage:
            self.storage[Bucket] = {}
        self.storage[Bucket][Key] = Body
        print(f"MOCK: File uploaded to {Bucket}/{Key}")
        return {}

# Initialize mock clients
s3_client = MockS3Client()

# S3 bucket configuration
S3_BUCKET_NAME = 'local-mock-bucket'
S3_RESUMES_PREFIX = 'resumes/'
S3_JD_PREFIX = 'job_descriptions/'
S3_AUDIO_PREFIX = 'audio_responses/'

def handler(event, context):
    print('received event:')
    print(event)
    
    path = event.get('path', '')
    
    if path == '/items':
        return process_file_upload(event, context)
    elif path == '/audio':
        return process_audio_upload(event, context)
    else:
        return {
            'statusCode': 404,
            'headers': create_cors_headers(),
            'body': json.dumps({'error': 'Not found'})
        }

def process_file_upload(event, context):
    """
    Process file uploads (resume or job description)
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
                body = base64.b64decode(body).decode('utf-8')
                
            # Get file content and file type from the form data
            form_data = parse_multipart_form(body, boundary)
            file_content = form_data.get('file', [''])[0]
            file_type = form_data.get('fileType', [''])[0]
            file_name = form_data.get('fileName', ['uploaded_file'])[0]
            
            # Validate inputs
            if not file_content:
                return create_response(400, {'error': 'No file content found in the request'})
            
            if file_type not in ['resume', 'jd']:
                return create_response(400, {'error': 'Invalid fileType specified. Must be "resume" or "jd".'})
            
            # Determine the S3 prefix based on file type
            s3_prefix = S3_RESUMES_PREFIX if file_type == 'resume' else S3_JD_PREFIX
            s3_object_name = os.path.join(s3_prefix, file_name)
            
            # Upload the file to mock S3
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_object_name,
                Body=file_content,
                ContentType='application/octet-stream'
            )
            
            return create_response(200, {
                'message': f"File '{file_name}' uploaded successfully as {file_type} to S3.",
                'filename': file_name,
                's3_key': s3_object_name
            })
        else:
            return create_response(400, {'error': 'Invalid content type. Must be multipart/form-data.'})
    
    except Exception as e:
        print(f"Error processing file upload: {str(e)}")
        return create_response(500, {'error': f"An error occurred: {str(e)}"})

def process_audio_upload(event, context):
    """
    Process audio uploads and return mock transcription
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
            timestamp = form_data.get('timestamp', ['timestamp'])[0]
            
            # Validate input
            if not audio_content:
                return create_response(400, {'error': 'No audio content found in the request'})
            
            # Generate a unique object name
            file_name = f"response_{timestamp.replace(':', '-').replace('.', '-')}.webm"
            s3_object_name = os.path.join(S3_AUDIO_PREFIX, file_name)
            
            # Upload the audio to mock S3
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
            
            # Mock transcription
            transcript = "This is a mock transcription of your audio response. In a real environment, this would be the result from Amazon Transcribe."
            
            return create_response(200, {
                'message': 'Audio response uploaded and transcribed successfully.',
                'filename': file_name,
                's3_key': s3_object_name,
                'transcript': transcript
            })
        else:
            return create_response(400, {'error': 'Invalid content type. Must be multipart/form-data.'})
    
    except Exception as e:
        print(f"Error processing audio upload: {str(e)}")
        return create_response(500, {'error': f"An error occurred: {str(e)}"})

def parse_multipart_form(body, boundary):
    """
    Parse multipart form data from the request body.
    """
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
            
            # If this is a file, handle filename
            if 'filename="' in part:
                filename = part.split('filename="')[1].split('"')[0]
                form_data['fileName'] = [filename]
            
            # Store the form field value
            if field_name in form_data:
                form_data[field_name].append(value)
            else:
                form_data[field_name] = [value]
    
    return form_data

def create_cors_headers():
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }

def create_response(status_code, body):
    """Create a standardized response for API Gateway."""
    return {
        'statusCode': status_code,
        'headers': create_cors_headers(),
        'body': json.dumps(body)
    }