#!/usr/bin/env python3

import os
import requests
from openai import OpenAI
from bs4 import BeautifulSoup

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


def fetch_spc_outlook():
    """Fetches the Day 1 SPC Outlook text from the SPC website."""
    url = "https://www.spc.noaa.gov/products/outlook/day1otlk.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # Ensure we notice bad responses

    soup = BeautifulSoup(response.content, "html.parser")

    # Find the main text content of the SPC Outlook
    outlook_text = ""
    for pre in soup.find_all("pre"):
        outlook_text += pre.get_text()

    return outlook_text


def summarize_forecast(forecast_text, spc_text):
    """Uses OpenAI to summarize the forecast with Markdown formatting."""
    system_content = (
        "You are a weather expert. Your job is to advise a storm chaser on "
        "what a good target is. You have extensive knowledge of severe weather "
        "including hodographs, soundings, and tornado forecasting."
    )

    user_content = (
        f"SPC Day One Outlook:\n{spc_text}\n"
        f"Forecast from the local MPX office:\n{forecast_text}\n"
        "Summarize the following forecast into the next three days. After that "
        "summary, I would like a summary of the rest of the AFD so I know how "
        "the period overall will be looking. Organize the list by date and "
        "format the days of the week in bold. Specifically, I am interested in "
        "where the storms will be, whether or not there will be supercells, if "
        "there is a tornado risk, and any other information that may be important "
        "from the AFD. Make sure to include what time the AFD was issued at. If "
        "the current date looks like there is tornado potential, go into depth "
        "about that forecast.\n\n"
        "We are also going to analyze the SPC Day 1 severe outlook. If it does not "
        "mention South Dakota, Minnesota, North Dakota, Iowa, or Wisconsin, we are "
        "not interested in it. If it is mentioned, please use that information as "
        "well as the AFD in your summary. At the end tell me which days you would "
        "choose to storm chase as if you were a storm chaser. Pretend that you are "
        "a very cringe dad pretending that he is a gen z using their slang to try to "
        "embarass his family. Use terms such as skibidi and rizz."
    )

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
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
    spc_dayone_text = fetch_spc_outlook()
    summary = summarize_forecast(forecast_text, spc_dayone_text)
    response = send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID, summary)
    print(f"Message sent to Telegram channel: {response.status_code}")
