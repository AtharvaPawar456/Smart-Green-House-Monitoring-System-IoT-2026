from datetime import datetime
from zoneinfo import ZoneInfo


def getAustralianTimestamp():
    """
    Get current Australia/Sydney timestamp.

    Returns:
        str: Formatted Sydney timestamp
    """
    try:
        australiaTime = datetime.now(ZoneInfo("Australia/Sydney"))

        formattedTime = australiaTime.strftime("%Y-%m-%d %H:%M:%S")

        print(f"Sydney Time: {formattedTime}")

        return formattedTime

    except Exception as error:
        print(f"error | timestamp generation failed | {error}")
        return None


getAustralianTimestamp()