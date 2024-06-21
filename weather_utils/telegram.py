# weather_utils/telegram.py

import requests


def send_telegram_message(token, channel_id, message):
    """Sends a message to a Telegram channel."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": channel_id, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    response.raise_for_status()  # Ensure we notice bad responses
    return response
