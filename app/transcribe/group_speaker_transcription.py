from typing import List
from datetime import datetime
import uuid


def group_speaker_transcriptions(transcriptions: List[dict]) -> List[dict]:
    """
    Groups consecutive words from the same speaker into complete phrases.

    Args:
        transcriptions: List of individual word transcriptions with speaker labels

    Returns:
        List of grouped transcriptions by speaker with complete phrases
    """
    if not transcriptions:
        return []

    grouped = []
    current_speaker = transcriptions[0]['agent_name']
    current_phrase = []
    start_time = transcriptions[0]['timestamp']

    for item in transcriptions:
        # If speaker changes or there's a significant pause (more than 1 second)
        time_diff = (datetime.strptime(item['timestamp'], "%Y-%m-%d %H:%M:%S.%f") -
                     datetime.strptime(start_time if current_phrase else item['timestamp'], "%Y-%m-%d %H:%M:%S.%f"))

        if (item['agent_name'] != current_speaker or
                (current_phrase and time_diff.total_seconds() > 1.0)):
            # Add the completed phrase to results
            if current_phrase:
                grouped.append({
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
            # Update end time to be the latest timestamp in the phrase
            start_time = min(start_time, item['timestamp'])

    # Add the last phrase
    if current_phrase:
        grouped.append({
            "id": str(uuid.uuid4()),
            "timestamp": start_time,
            "agent_name": current_speaker,
            "content": ' '.join(current_phrase)
        })

    return grouped


# Example usage with your data:
