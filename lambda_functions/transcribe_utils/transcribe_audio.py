import boto3
import os
import json
import time
import requests

# Initialize AWS clients
# In Lambda, these will be initialized with the Lambda's role permissions
transcribe_client = boto3.client('transcribe')

def transcribe_audio_file(s3_bucket, s3_key):
    """
    Transcribe an audio file from S3 using Amazon Transcribe
    
    Args:
        s3_bucket (str): The S3 bucket name where the audio file is stored
        s3_key (str): The S3 object key (path) to the audio file
        
    Returns:
        str: The transcribed text, or None if transcription failed
    """
    try:
        # Generate a unique job name based on the file name
        job_name = f"transcription-{int(time.time())}-{os.path.basename(s3_key)}"
        # Ensure job name meets AWS requirements (alphanumeric and hyphens only)
        job_name = ''.join(c if c.isalnum() or c == '-' else '-' for c in job_name)
        # Truncate if too long (max 200 chars for job name)
        job_name = job_name[:200]
        
        # Start transcription job
        response = transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{s3_bucket}/{s3_key}'},
            MediaFormat='webm',
            LanguageCode='en-US'
        )
        
        # Wait for transcription to complete (with timeout)
        max_tries = 60  # 5 minutes timeout (checking every 5 seconds)
        tries = 0
        
        while tries < max_tries:
            status = transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
                
            tries += 1
            time.sleep(5)
        
        if tries >= max_tries:
            print(f"Transcription job {job_name} timed out")
            return None
        
        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            # Get the transcript
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            transcript_response = requests.get(transcript_uri)
            transcript_data = transcript_response.json()
            
            # Extract the transcript text
            transcript_text = transcript_data['results']['transcripts'][0]['transcript']
            
            # Delete the transcription job to clean up
            transcribe_client.delete_transcription_job(
                TranscriptionJobName=job_name
            )
            
            return transcript_text
        else:
            failure_reason = status['TranscriptionJob'].get('FailureReason', 'Unknown reason')
            print(f"Transcription failed: {failure_reason}")
            return None
            
    except Exception as e:
        print(f"Error in transcription: {str(e)}")
        return None 