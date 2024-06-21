# weather_utils/summarizing.py

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_forecast(forecast_text):
    """Uses OpenAI to summarize the forecast with Markdown formatting."""
    system_content = (
        "You are a weather expert. Your job is to advise a storm chaser on "
        "what a good target is. You have extensive knowledge of severe weather "
        "including hodographs, soundings, and tornado forecasting."
    )

    user_content = (
        f"Forecast from the local MPX office:\n{forecast_text}\n"
        "Summarize the area forecast discussion that was provided."
        "Split the summary into each day mentioned as well as the long term"
        "I have a particular interest in the storm portion of the forecast, make sure that is emphasized in the day by day summary."
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
