# weather_utils/fetching.py

import requests
from bs4 import BeautifulSoup

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
