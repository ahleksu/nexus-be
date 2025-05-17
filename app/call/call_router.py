from datetime import datetime

from fastapi import FastAPI, HTTPException, APIRouter
import boto3
import uuid

from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(
    prefix="/call",
    tags=["call"]
)

# Initialize Chime client
chime_sdk = boto3.client(
    'chime-sdk-meetings',
    region_name='ap-southeast-1',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

# In-memory storage for hackathon
meetings_db = {}


class CreateMeetingRequest(BaseModel):
    agent_id: str


@router.post("/create-meeting")
async def create_meeting(request: CreateMeetingRequest):
    """Create a new one-on-one meeting"""
    try:
        meeting_id = str(uuid.uuid4())
        external_meeting_id = f"meeting-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Create meeting with required parameters
        meeting_response = chime_sdk.create_meeting(
            ClientRequestToken=meeting_id,
            MediaRegion='ap-southeast-1',
            ExternalMeetingId=external_meeting_id,  # Required parameter
            MeetingFeatures={
                'Audio': {'EchoReduction': 'AVAILABLE'}
            }
        )

        # Create agent attendee
        agent_attendee = chime_sdk.create_attendee(
            MeetingId=meeting_response['Meeting']['MeetingId'],
            ExternalUserId=f"agent-{request.agent_id}"
        )

        # Create customer attendee
        customer_attendee = chime_sdk.create_attendee(
            MeetingId=meeting_response['Meeting']['MeetingId'],
            ExternalUserId=f"customer-{uuid.uuid4()}"
        )

        # Store meeting data
        meetings_db[meeting_id] = {
            'meeting': meeting_response['Meeting'],
            'agent_attendee': agent_attendee['Attendee'],
            'customer_attendee': customer_attendee['Attendee'],
            'external_meeting_id': external_meeting_id
        }

        return {
            "meeting_id": meeting_id,
            "agent_join_data": {
                "meeting": meeting_response['Meeting'],
                "attendee": agent_attendee['Attendee']
            },
            "customer_join_link": f"/get-customer-join-data/{meeting_id}",
            "external_meeting_id": external_meeting_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-customer-join-data/{meeting_id}")
async def get_customer_join_data(meeting_id: str):
    """Get customer join data"""
    try:
        meeting_data = meetings_db.get(meeting_id)
        if not meeting_data:
            raise HTTPException(status_code=404, detail="Meeting not found")

        return {
            "meeting": meeting_data['meeting'],
            "attendee": meeting_data['customer_attendee']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meeting-info/{meeting_id}")
async def get_meeting_info(meeting_id: str):
    """Check meeting status"""
    if meeting_id not in meetings_db:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return {"status": "active", "meeting_id": meeting_id}