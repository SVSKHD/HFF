from datetime import datetime
from utils import connect_mt5

def main():
    # Get the current time
    today = datetime.now()
    connect = connect_mt5()
    if connect:
        # Check if the current time is between 12:00 AM (midnight) and 12:00 PM (noon)
        if 0 <= today.hour < 12:
            print("Trading is allowed")
        else:
            print("Monitoring")


if __name__ == "__main__":
    main()