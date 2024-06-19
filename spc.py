#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup


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


if __name__ == "__main__":
    outlook_text = fetch_spc_outlook()
    print(outlook_text)
