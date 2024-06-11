#!/usr/bin/env python3

import os
import requests
from openai import OpenAI

# Environment variables for Telegram and OpenAI
TELEGRAM_TOKEN = os.getenv("TELEGRAM_KEY")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def fetch_latest_afd():
    """Fetches the latest Area Forecast Discussion for Minnesota."""
    url = "https://api.weather.gov/products/types/afd/locations/mpx"
    headers = {"User-Agent": "Python"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # Ensure we notice bad responses
    latest_afd = response.json()["@graph"][0]["@id"]
    afd_txt = requests.get(latest_afd, headers=headers, timeout=10)
    afd_txt.raise_for_status()  # Ensure we notice bad responses
    afd_json = afd_txt.json()
    return afd_json["productText"]


def summarize_forecast(forecast_text):
    """Uses OpenAI to summarize the forecast with Markdown formatting."""
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a weather expert. Your job is to advise a storm chaser on what a good target is. "
                    "You have extensive knowledge of severe weather including hodographs, soundings, and tornado forecasting."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Summarize the following forecast into the next three days. After that summary I would like a summary of the rest of the AFD so I know how the period overall will be looking. Organize the list by date and format the days of the week in bold. Specifically I am interested in where the storms will be, whether or not there will be supercells, if there is a tornado risk, and any other information that may be important from the AFD.:\n\n"
                    f"Forecast:\n{forecast_text}"
                ),
            },
        ],
        max_tokens=1000,
        temperature=0.5,
    )
    summary = completion.choices[0].message.content

    # Add Markdown formatting to days of the week
    summary = summary.replace("Monday:", "*Monday:*")
    summary = summary.replace("Tuesday:", "*Tuesday:*")
    summary = summary.replace("Wednesday:", "*Wednesday:*")
    summary = summary.replace("Thursday:", "*Thursday:*")
    summary = summary.replace("Friday:", "*Friday:*")
    summary = summary.replace("Saturday:", "*Saturday:*")
    summary = summary.replace("Sunday:", "*Sunday:*")

    return summary


def send_telegram_message(token, channel_id, message):
    """Sends a message to a Telegram channel."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": channel_id, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    response.raise_for_status()  # Ensure we notice bad responses
    return response


if __name__ == "__main__":
    forecast_text = fetch_latest_afd()
    summary = summarize_forecast(forecast_text)
    response = send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID, summary)
    print(f"Message sent to Telegram channel: {response.status_code}")
