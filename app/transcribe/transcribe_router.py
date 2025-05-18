import asyncio
import time

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, APIRouter
from fastapi.responses import JSONResponse
import boto3
from datetime import datetime
import uuid
from typing import List
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
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


@router.get("/helper/{job_id}")
async def helper(job_id: str):
    """Check status of a transcription job and get assistant response in one call"""
    try:
        # 1. First get the transcription status
        status = transcribe_client.get_transcription_job(TranscriptionJobName=job_id)
        job_status = status['TranscriptionJob']['TranscriptionJobStatus']

        if job_status == 'IN_PROGRESS':
            return JSONResponse(content={"status": "in_progress"}, status_code=200)

        if job_status == 'FAILED':
            raise HTTPException(
                status_code=500,
                detail=status['TranscriptionJob'].get('FailureReason', 'Unknown error')
            )

        # 2. Get the transcript
        transcript_key = f"transcriptions/{job_id}.json"
        cloudfront_url = f"https://d2wvh13x6zr3i2.cloudfront.net/{transcript_key}"

        response = requests.get(cloudfront_url, timeout=10)
        response.raise_for_status()
        transcript_response = response.json()

        # 3. Process transcript into compact format
        word_items = []
        for item in transcript_response.get('results', {}).get('items', []):
            if item.get('type') == 'pronunciation' and 'start_time' in item:
                word_items.append({
                    "agent_name": item.get('speaker_label', 'spk_0'),
                    "content": item['alternatives'][0]['content']
                })

        # Group into phrases
        grouped_transcriptions = []
        if word_items:
            current_speaker = word_items[0]['agent_name']
            current_phrase = []

            for item in word_items:
                if item['agent_name'] != current_speaker:
                    if current_phrase:
                        grouped_transcriptions.append({
                            "agent_name": current_speaker,
                            "content": ' '.join(current_phrase)
                        })
                    current_speaker = item['agent_name']
                    current_phrase = [item['content']]
                else:
                    current_phrase.append(item['content'])

            if current_phrase:
                grouped_transcriptions.append({
                    "agent_name": current_speaker,
                    "content": ' '.join(current_phrase)
                })

        compact_transcript = "\n".join(
            [f"{item['agent_name']} - {item['content']}"
             for item in grouped_transcriptions]
        )

        # 4. Create thread and message
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=compact_transcript
        )

        # 5. Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions=(
                "You are a smart assistant for a customer support agent. "
                "Customer support will accept calls that will be transcribed real-time. "
                "During the conversation, find meaningful insights that can help the agent with their responses. "
                "Always look for relevant information in the document files that are uploaded and follow these rules:\n"
                "1. Create engaging responses in Markdown format\n"
                "2. Always add references to information you have extracted\n"
                "3. Filter, assess, and rank the best response you can suggest to the agent"
            )
        )

        # Wait for completion
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                raise HTTPException(
                    status_code=500,
                    detail=f"Assistant run failed: {run_status.last_error}"
                )
            await asyncio.sleep(1)

        # 6. Get assistant response
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_messages = [
            msg for msg in messages.data
            if msg.role == "assistant"
        ]

        if not assistant_messages:
            raise HTTPException(
                status_code=500,
                detail="No response from assistant"
            )

        return {
            "transcript": compact_transcript,
            "assistant_response": assistant_messages[0].content[0].text.value,
            "thread_id": thread.id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process request: {str(e)}"
        )
# Initialize OpenAI client
api_key = settings.OPENAI_API_KEY
client = OpenAI(api_key=api_key)

# Assistant and Thread IDs
assistant_id = "asst_BLo4eW6f3AOQgfiwO0dCcP8e"
thread_id = "your-thread-id"  # You're creating a new thread now, so this might not be needed
vector_store_id = "vs_68291cba43e881918053971d1ca979f0"


async def create_message(content):
    """Helper function to create a message in the assistant thread"""
    try:
        # Create a new thread for each conversation
        new_thread = client.beta.threads.create()

        # Ensure content is a string and not too long
        if isinstance(content, (list, dict)):
            content = str(content)

        # Truncate content if it's too long (OpenAI has limits)
        max_length = 32768  # OpenAI's maximum message length
        if len(content) > max_length:
            content = content[:max_length] + "... [truncated]"

        message = client.beta.threads.messages.create(
            thread_id=new_thread.id,
            role="user",
            content=content
        )

        # Return both thread and message info
        return {
            "thread_id": new_thread.id,
            "message": message,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create message: {str(e)}"
        )


async def run_assistant(thread_id: str):
    """Helper function to run the assistant on a specific thread"""
    try:
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions=(
                "You are a smart assistant for a customer support agent. "
                "Customer support will accept calls that will be transcribed real-time. "
                "During the conversation, find meaningful insights that can help the agent with their responses. "
                "Always look for relevant information in the document files that are uploaded and follow these rules:\n"
                "1. Create engaging responses in Markdown format\n"
                "2. Always add references to information you have extracted\n"
                "3. Filter, assess, and rank the best response you can suggest to the agent"
            )
        )

        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                return {"error": f"Run failed: {run_status.last_error}"}
            await asyncio.sleep(2)

        # Retrieve the assistant's response
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )

        return {
            "success": True,
            "messages": messages.data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run assistant: {str(e)}"
        )