from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, APIRouter
from fastapi.responses import JSONResponse
import boto3
from datetime import datetime
import uuid
from typing import List
import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel

from app.core.config import settings

# Load environment variables
load_dotenv()


# Define your Pydantic model
class CallTranscriptionType(BaseModel):
    timestamp: str
    agent_name: str
    content: str
    id: str

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2023-01-01 12:00:00",
                "agent_name": "spk_0",
                "content": "Hello, how can I help you?",
                "id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


# Initialize FastAPI
router = APIRouter(
    prefix="/transcribe",
    tags=["call"]
)

# Configure AWS client
transcribe_client = boto3.client(
    'transcribe',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name="ap-southeast-1"
)

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name="ap-southeast-1"
)


@router.post("/", response_model=List[CallTranscriptionType])
async def transcribe_audio(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(..., description="Audio file to transcribe (MP3, WAV, FLAC)")
):
    """
    Transcribe an audio file using AWS Transcribe service.

    Returns:
        List of transcription segments with speaker identification.
    """
    # Validate file type
    valid_extensions = ('.wav', '.mp3', '.mp4', '.flac')
    if not file.filename.lower().endswith(valid_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(valid_extensions)}"
        )

    # Generate unique IDs
    job_name = f"transcribe_{uuid.uuid4().hex}"
    file_extension = os.path.splitext(file.filename)[1]
    s3_key = f"audio-uploads/{job_name}{file_extension}"

    try:
        # Upload to S3
        bucket_name = settings.AWS_BUCKET_NAME

        # For production, you might want to create the bucket if it doesn't exist
        s3_client.upload_fileobj(file.file, bucket_name, s3_key)

        # Start transcription job
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f"s3://{bucket_name}/{s3_key}"},
            MediaFormat=file_extension[1:],  # Remove the dot
            LanguageCode='en-US',
            Settings={
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels': 2,
                'ChannelIdentification': False
            },
            OutputBucketName=bucket_name,  # Store output in same bucket
            OutputKey=f"transcriptions/{job_name}.json"
        )

        # In production, use SNS notifications instead of polling
        def check_transcription_status(job_name: str):
            while True:
                status = transcribe_client.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                if job_status in ['COMPLETED', 'FAILED']:
                    break

        background_tasks.add_task(check_transcription_status, job_name)

        # Return immediate response with job ID
        return JSONResponse(
            content={
                "message": "Transcription started",
                "job_id": job_name,
                "status_check": f"/transcription-status/{job_name}"
            },
            status_code=202
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.get("/transcription-status/{job_id}", response_model=List[CallTranscriptionType])
async def get_transcription_status(job_id: str):
    """Check status of a transcription job using CloudFront distribution"""
    try:
        # First check the job status
        status = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_id
        )

        job_status = status['TranscriptionJob']['TranscriptionJobStatus']

        if job_status == 'IN_PROGRESS':
            return JSONResponse(
                content={"status": "in_progress"},
                status_code=200
            )

        if job_status == 'FAILED':
            raise HTTPException(
                status_code=500,
                detail=status['TranscriptionJob'].get('FailureReason', 'Unknown error')
            )

        # Use CloudFront URL instead of direct S3 URL
        transcript_key = f"transcriptions/{job_id}.json"
        cloudfront_url = f"https://d2wvh13x6zr3i2.cloudfront.net/{transcript_key}"

        try:
            response = requests.get(
                cloudfront_url,
                timeout=10
            )
            response.raise_for_status()

            if not response.content:
                raise HTTPException(
                    status_code=502,
                    detail="Empty response from transcription service"
                )

            transcript_response = response.json()

        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch transcript from CloudFront: {str(e)}"
            )

        # Process individual word items
        word_items = []
        for item in transcript_response.get('results', {}).get('items', []):
            if item.get('type') == 'pronunciation' and 'start_time' in item:
                word_items.append({
                    "id": str(uuid.uuid4()),
                    "timestamp": format_timestamp(item['start_time']),
                    "agent_name": item.get('speaker_label', 'spk_0'),
                    "content": item['alternatives'][0]['content']
                })

        # Group words into complete phrases by speaker
        grouped_transcriptions = []
        if word_items:
            current_speaker = word_items[0]['agent_name']
            current_phrase = []
            start_time = word_items[0]['timestamp']

            for item in word_items:
                # Calculate time difference
                current_time = parse_datetime(item['timestamp'])
                last_time = parse_datetime(start_time if current_phrase else item['timestamp'])
                time_diff = (current_time - last_time).total_seconds()

                # If speaker changes or significant pause (>1 second)
                if (item['agent_name'] != current_speaker or
                        (current_phrase and time_diff > 1.0)):
                    # Add completed phrase
                    if current_phrase:
                        grouped_transcriptions.append({
                            "id": str(uuid.uuid4()),
                            "timestamp": start_time,
                            "agent_name": current_speaker,
                            "content": ' '.join(current_phrase)
                        })

                    # Start new phrase
                    current_speaker = item['agent_name']
                    current_phrase = [item['content']]
                    start_time = item['timestamp']
                else:
                    # Continue current phrase
                    current_phrase.append(item['content'])

            # Add the last phrase
            if current_phrase:
                grouped_transcriptions.append({
                    "id": str(uuid.uuid4()),
                    "timestamp": start_time,
                    "agent_name": current_speaker,
                    "content": ' '.join(current_phrase)
                })

        return grouped_transcriptions

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get transcription status: {str(e)}"
        )


def format_timestamp(seconds: float) -> str:
    """Convert seconds to formatted timestamp string"""
    dt = datetime.fromtimestamp(float(seconds))
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")


def parse_datetime(timestamp_str: str) -> datetime:
    """Parse timestamp string that may or may not have milliseconds"""
    try:
        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

@router.get("/")
async def health_check():
    return {"status": "healthy", "service": "audio-transcription-api"}