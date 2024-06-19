#!/usr/bin/env python3

import os
import time
import requests
from openai import OpenAI
from bs4 import BeautifulSoup

# Environment variables for Telegram and OpenAI
TELEGRAM_TOKEN = os.getenv("TELEGRAM_KEY")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Global Variables
AFD_URL = "https://api.weather.gov/products/types/afd/locations/mpx"
SPC_BASE_URL = "https://www.spc.noaa.gov/products/outlook/"
DAY1_URL = f"{SPC_BASE_URL}day1otlk.html"
DAY2_URL = f"{SPC_BASE_URL}day2otlk.html"
DAY3_URL = f"{SPC_BASE_URL}day3otlk.html"
DAYS4_TO_8_URL = f"{SPC_BASE_URL}day3otlk.html"

def fetch_latest_afd(use_local=False):
    """Fetches the latest Area Forecast Discussion for Minnesota."""
    if use_local and os.path.exists("latest_afd.json"):
        with open("latest_afd.json", "r") as file:
            return file.read()
    else:
        headers = {"User-Agent": "Python"}
        response = requests.get(AFD_URL, headers=headers, timeout=10)
        response.raise_for_status()
        latest_afd_id = response.json()["@graph"][0]["@id"]
        afd_txt = requests.get(latest_afd_id, headers=headers, timeout=10)
        afd_txt.raise_for_status()
        afd_json = afd_txt.json()
        afd_text = afd_json["productText"]

        # Save the response locally
        with open("latest_afd.json", "w") as file:
            file.write(afd_text)
        return afd_text

def fetch_spc_outlook(day, use_local=False):
    """Fetches the SPC Outlook text from the SPC website."""
    urls = {
        1: DAY1_URL,
        2: DAY2_URL,
        3: DAY3_URL,
        4: DAYS4_TO_8_URL
    }
    url = urls.get(day)
    
    if use_local and os.path.exists(f"day{day}_spc_outlook.html"):
        with open(f"day{day}_spc_outlook.html", "r") as file:
            return file.read()
    else:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        outlook_text = "\n".join(pre.get_text() for pre in soup.find_all("pre"))
        
        # Save the response locally
        with open(f"day{day}_spc_outlook.html", "w") as file:
            file.write(outlook_text)
        return outlook_text

def summarize_forecast(forecast_text, spc_text):
    """Uses OpenAI to summarize the forecast with Markdown formatting."""
    system_content = (
        "You are a weather expert. Your job is to advise a storm chaser on "
        "what a good target is. You have extensive knowledge of severe weather "
        "including hodographs, soundings, and tornado forecasting."
    )

    user_content = (
        f"SPC Day One Outlook:\n{spc_text[1]}\n"
        f"SPC Day Two Outlook:\n{spc_text[2]}\n"
        f"SPC Day Three Outlook:\n{spc_text[3]}\n"
        f"SPC Days Four to Eight Outlook:\n{spc_text[4]}\n"
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
        "choose to storm chase as if you were a storm chaser."
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
    summary = completion.choices[0].message['content']

    # Add Markdown formatting to days of the week
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in days:
        summary = summary.replace(f"{day}:", f"*{day}:*")

    return summary

def send_telegram_message(token, channel_id, message):
    """Sends a message to a Telegram channel."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": channel_id, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response

def main(use_local_files=False):
    forecast_text = fetch_latest_afd(use_local=use_local_files)
    spc_text = [fetch_spc_outlook(day, use_local=use_local_files) for day in range(1, 5)]
    
    # Adding a delay between requests
    time.sleep(5)
    
    summary = summarize_forecast(forecast_text, spc_text)
    response = send_telegram_message(TELEGRAM_TOKEN, TELEGrah CHANNEL_ID, summary)
    print(f"Message sent to Telegram channel: {response.status_code}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch and summarize weather forecasts.")
    parser.add_argument("--local", action="store_true", help="Use local files instead of fetching from the web")
    args = parser.parse_args()
    
    main(use_local_files=args.local)
