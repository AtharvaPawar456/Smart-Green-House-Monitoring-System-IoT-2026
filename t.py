from datetime import datetime
from zoneinfo import ZoneInfo


def getAustralianTimestamp():
    """
    Return current Australia/Sydney timestamp.
    """
    try:
        australiaTime = datetime.now(ZoneInfo("Australia/Sydney"))

        print("Australian Timestamp:")
        print(australiaTime.strftime("%Y-%m-%d %H:%M:%S"))

    except Exception as error:
        print(f"error | timestamp generation failed | {error}")


getAustralianTimestamp()