# Voice Assistant

A Python-based voice assistant that can perform various tasks through voice commands.

## Features

- Speech recognition and text-to-speech capabilities
- Weather information retrieval
- News updates
- Web searches
- YouTube video playback
- Email sending
- Time and date information
- And more!

## Prerequisites

- Python 3.7 or higher
- Microphone
- Internet connection
- API keys for:
  - News API
  - OpenWeatherMap API
  - Gmail account (for email functionality)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd voice-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your API keys and credentials:
```
NEWS_API_KEY=your_news_api_key_here
WEATHER_API_KEY=your_weather_api_key_here
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_email_password_here
```

## Usage

1. Run the voice assistant:
```bash
python voice_assistant_v2.py
```

2. Available voice commands:
- "Hello" or "Hi" - Greeting
- "What's the time?" - Get current time
- "What's the date?" - Get current date
- "Tell me the news" - Get latest news
- "What's the weather in [city]?" - Get weather information
- "Search for [query]" - Perform a web search
- "Play [video name]" - Play a YouTube video
- "Send email" - Send an email
- "Exit" or "Bye" - Exit the program

## Error Handling

The assistant includes comprehensive error handling for:
- Speech recognition issues
- Network connectivity problems
- API request failures
- Invalid commands

## Logging

Logs are generated with timestamps and can be found in the console output. This helps in debugging and monitoring the assistant's behavior.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 