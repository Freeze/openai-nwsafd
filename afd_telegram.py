#!/usr/bin/env python3

import requests
import os
from weather_utils import telegram, summarizing, file_utils

# Constants
URL = "https://api.weather.gov/products/types/afd/locations/mpx"
DATA_DIR = "data"
TIMESTAMP_FILE = os.path.join(DATA_DIR, "last_afd_timestamp.txt")
AFD_FILE = os.path.join(DATA_DIR, "latest_afd.txt")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_KEY")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


def fetch_latest_afd():
    """Fetch the latest Area Forecast Discussion from the API."""
    response = requests.get(URL)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()
    return data["@graph"]


def get_last_fetched_timestamp():
    """Retrieve the last fetched AFD timestamp from the local file."""
    if os.path.exists(TIMESTAMP_FILE):
        with open(TIMESTAMP_FILE, "r") as file:
            return file.read().strip()
    return None


def save_last_fetched_timestamp(timestamp):
    """Save the last fetched AFD timestamp to the local file."""
    with open(TIMESTAMP_FILE, "w") as file:
        file.write(timestamp)


def save_afd_to_file(afd_text):
    """Save the AFD text to a local file."""
    with open(AFD_FILE, "w") as file:
        file.write(afd_text)


def main():
    """Main function to fetch and display the latest AFD if new."""
    # Fetch the latest AFDs
    afds = fetch_latest_afd()

    # Sort AFDs by issuance time in descending order
    afds.sort(key=lambda x: x["issuanceTime"], reverse=True)

    # Get the latest AFD issuance time
    latest_afd = afds[0]
    latest_timestamp = latest_afd["issuanceTime"]

    # Get the last fetched timestamp from the local file
    last_fetched_timestamp = get_last_fetched_timestamp()

    # Compare timestamps and fetch new AFD if there is a new one
    if last_fetched_timestamp is None or latest_timestamp > last_fetched_timestamp:
        print("New AFD available:", latest_afd)
        save_last_fetched_timestamp(latest_timestamp)

        # Fetch the latest AFD text
        afd_url = latest_afd["@id"]
        afd_response = requests.get(afd_url)
        afd_response.raise_for_status()
        afd_text = afd_response.json()["productText"]

        # Save the AFD text to a local file
        save_afd_to_file(afd_text)

        # Summarize the forecast
        summary = summarizing.summarize_forecast(afd_text)

        # Create the message with the summary and the URL
        message = f"{summary}\n\nRead the full AFD here: https://forecast.weather.gov/product.php?site=MPX&issuedby=MPX&product=AFD&format=ci&version=1&glossary=1"

        # Debugging: Print values
        print(f"TELEGRAM_TOKEN: {TELEGRAM_TOKEN}")
        print(f"TELEGRAM_CHANNEL_ID: {TELEGRAM_CHANNEL_ID}")
        print(f"Summary: {summary}")
        print(f"AFD URL: https://forecast.weather.gov/product.php?site=MPX&issuedby=MPX&product=AFD&format=ci&version=1&glossary=1")

        # Send the summary and URL to Telegram
        try:
            response = telegram.send_telegram_message(
                TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID, message
            )
            print(f"Message sent to Telegram channel: {response.status_code}")
        except requests.exceptions.HTTPError as e:
            print(f"Failed to send message: {e}")
            print(f"Response content: {e.response.content}")

    else:
        print("No new AFD available.")


if __name__ == "__main__":
    main()
