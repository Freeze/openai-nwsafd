#!/usr/bin/env python3

import os
import requests
import time
import argparse
from openai import OpenAI
from bs4 import BeautifulSoup

# Environment variables for Telegram and OpenAI
TELEGRAM_TOKEN = os.getenv("TELEGRAM_KEY")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# URLs for SPC Outlooks
URLS = {
    "day1": "https://www.spc.noaa.gov/products/outlook/day1otlk.html",
    "day2": "https://www.spc.noaa.gov/products/outlook/day2otlk.html",
    "day3": "https://www.spc.noaa.gov/products/outlook/day3otlk.html",
    "day4-8": "https://www.spc.noaa.gov/products/exper/day4-8/",
}


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


def fetch_spc_outlook(day):
    """Fetches the SPC Outlook text for a given day from the SPC website."""
    url = URLS[day]
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # Ensure we notice bad responses

    soup = BeautifulSoup(response.content, "html.parser")

    # Find the main text content of the SPC Outlook
    outlook_text = ""
    for pre in soup.find_all("pre"):
        outlook_text += pre.get_text()

    return outlook_text


def summarize_forecast(forecast_text, spc_texts):
    """Uses OpenAI to summarize the forecast with Markdown formatting."""
    system_content = (
        "You are a weather expert. Your job is to advise a storm chaser on "
        "what a good target is. You have extensive knowledge of severe weather "
        "including hodographs, soundings, and tornado forecasting."
    )

    user_content = (
        f"SPC Day One Outlook:\n{spc_texts.get('day1', 'Not available')}\n\n"
        f"SPC Day Two Outlook:\n{spc_texts.get('day2', 'Not available')}\n\n"
        f"SPC Day Three Outlook:\n{spc_texts.get('day3', 'Not available')}\n\n"
        f"SPC Day Four to Eight Outlook:\n{spc_texts.get('day4-8', 'Not available')}\n\n"
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
        "We are also going to analyze the SPC Day 1, Day 2, Day 3, and Day 4-8 severe outlooks. "
        "If they do not mention South Dakota, Minnesota, North Dakota, Iowa, or Wisconsin, we are "
        "not interested in them. If they are mentioned, please use that information as well as the AFD "
        "in your summary. At the end, tell me which days you would choose to storm chase as if you were a storm chaser."
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


def save_to_file(filename, content):
    """Saves the given content to a file."""
    with open(filename, "w") as file:
        file.write(content)


def load_from_file(filename):
    """Loads content from a file."""
    with open(filename, "r") as file:
        return file.read()


def main(use_local_files):
    if use_local_files:
        forecast_text = load_from_file("afd.txt")
        spc_texts = {
            "day1": load_from_file("spc_day1.txt"),
            "day2": load_from_file("spc_day2.txt"),
            "day3": load_from_file("spc_day3.txt"),
            "day4-8": load_from_file("spc_day4-8.txt"),
        }
    else:
        forecast_text = fetch_latest_afd()
        save_to_file("afd.txt", forecast_text)

        spc_texts = {}
        for day in URLS.keys():
            spc_texts[day] = fetch_spc_outlook(day)
            save_to_file(f"spc_{day}.txt", spc_texts[day])
            time.sleep(5)  # Pause for 5 seconds between each request

    summary = summarize_forecast(forecast_text, spc_texts)
    response = send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID, summary)
    print(f"Message sent to Telegram channel: {response.status_code}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch and summarize weather forecasts."
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Read data from local files instead of fetching from the web",
    )
    args = parser.parse_args()

    main(use_local_files=args.local)
