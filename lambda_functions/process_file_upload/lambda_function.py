import json
import boto3
import os
import base64
from urllib.parse import parse_qs

# Initialize AWS clients
s3_client = boto3.client('s3')

# S3 bucket configuration - will be set via environment variables in Lambda
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
S3_RESUMES_PREFIX = 'resumes/'
S3_JD_PREFIX = 'job_descriptions/'

def lambda_handler(event, context):
    """
    AWS Lambda function to handle file uploads (resume or job description).
    This function is triggered by API Gateway and receives file data and type.
    
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
            
            # Upload the file to S3
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_object_name,
                Body=file_content,
                ContentType='application/octet-stream'  # This should be the actual MIME type if known
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
        field_name = part.split('name="')[1].split('"')[0]
        
        # Get the content after the double newline
        content = part.split('\r\n\r\n', 1)
        if len(content) > 1:
            value = content[1].strip()
            
            # If this is a file, we would handle the binary content appropriately
            if 'filename="' in part:
                filename = part.split('filename="')[1].split('"')[0]
                form_data['fileName'] = [filename]
            
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