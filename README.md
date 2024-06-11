
# Weather Forecast Summarizer and Telegram Notifier
(yes I made chatGPT write most of this for me)

This project provides a script to fetch the latest Area Forecast Discussion (AFD) for Minnesota, summarize the forecast using OpenAI's GPT-3.5-turbo model, and send the summarized forecast to a specified Telegram channel. The summary focuses on storm chasing insights, making it ideal for storm chasers.

## Features
- Fetches the latest AFD from the National Weather Service.
- Summarizes the forecast for the next three days, focusing on storm potential and locations relative to Saint Paul, MN.
- Sends the summarized forecast to a Telegram channel with formatted text.

## Prerequisites
- Python 3.6 or higher
- A Telegram bot token and channel ID
- OpenAI API key

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/weather-forecast-summarizer.git
   cd weather-forecast-summarizer
   ```

2. **Set up a virtual environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory of your project with the following content:
   ```env
   TELEGRAM_KEY=your-telegram-bot-token
   TELEGRAM_CHANNEL_ID=your-telegram-channel-id
   OPENAI_API_KEY=your-openai-api-key
   ```

## Usage

Activate the virtual environment if it's not already activated:
```sh
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Run the script:
```sh
python3 wxOpenAI.py
```

## Script Overview

The script performs the following steps:
1. Fetches the latest Area Forecast Discussion (AFD) for Minnesota from the National Weather Service.
2. Summarizes the forecast using OpenAI's GPT-3.5-turbo model, focusing on storm potential and locations relative to Saint Paul, MN.
3. Sends the summarized forecast to a specified Telegram channel with formatted text for better readability.

### fetch_latest_afd

Fetches the latest AFD for Minnesota.

### summarize_forecast

Uses OpenAI to summarize the forecast, focusing on storm potential and locations.

### send_telegram_message

Sends a message to a specified Telegram channel.

## Example

The summarized forecast will be sent to your Telegram channel with the days of the week formatted in bold for better readability.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [OpenAI](https://www.openai.com) for the GPT-3.5-turbo model.
- [National Weather Service](https://www.weather.gov) for providing the Area Forecast Discussion data.
- [Telegram](https://telegram.org) for their messaging platform and bot API.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
