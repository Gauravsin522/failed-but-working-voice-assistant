import os
import logging
from typing import Optional, Dict, Any
import speech_recognition as sr
import pyttsx3
from datetime import datetime
import webbrowser
import re
from urllib.parse import quote
import pywhatkit
import requests
from plyer import notification
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class VoiceAssistant:
    def __init__(self):
        """Initialize the Voice Assistant with necessary configurations."""
        self.context_memory: Dict[str, Any] = {}
        self.user_data_file = "user_data.json"
        self._setup_tts_engine()
        self.recognizer = sr.Recognizer()
        
        # Load API keys from environment variables
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.weather_api_key = os.getenv('WEATHER_API_KEY')
        self.email = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        if not all([self.news_api_key, self.weather_api_key, self.email, self.email_password]):
            logger.warning("Some API keys are missing. Please check your .env file.")

    def _setup_tts_engine(self) -> None:
        """Set up the text-to-speech engine with desired properties."""
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)  # Female voice
        self.engine.setProperty('rate', 150)  # Speed
        self.engine.setProperty('volume', 1.0)  # Volume

    def speak(self, text: str) -> None:
        """Convert text to speech and play it."""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")

    def recognize_speech(self) -> Optional[str]:
        """Recognize speech from microphone input."""
        with sr.Microphone() as source:
            logger.info("Listening...")
            try:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio)
                logger.info(f"You said: {text}")
                return text.lower()
            except sr.WaitTimeoutError:
                logger.warning("No speech detected within timeout")
                self.speak("I didn't hear anything. Please try again.")
            except sr.UnknownValueError:
                logger.warning("Speech was not understood")
                self.speak("Sorry, I couldn't understand that. Please try again.")
            except sr.RequestError as e:
                logger.error(f"Could not request results: {e}")
                self.speak("Network error. Please check your internet connection.")
            except Exception as e:
                logger.error(f"Unexpected error in speech recognition: {e}")
                self.speak("An unexpected error occurred. Please try again.")
        return None

    def get_news(self) -> None:
        """Fetch and speak the latest news."""
        if not self.news_api_key:
            self.speak("News API key is not configured.")
            return

        try:
            url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={self.news_api_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if "articles" in data:
                articles = data["articles"][:3]
                for i, article in enumerate(articles, 1):
                    self.speak(f"News {i}: {article['title']}")
            else:
                self.speak("Sorry, I couldn't fetch the news at the moment.")
        except requests.RequestException as e:
            logger.error(f"Error fetching news: {e}")
            self.speak("Sorry, I couldn't fetch the news at the moment.")

    def get_weather(self, city: str = "Delhi") -> None:
        """Fetch and speak weather information for a given city."""
        if not self.weather_api_key:
            self.speak("Weather API key is not configured.")
            return

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={quote(city)}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data.get("cod") == 200:
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                self.speak(f"The current temperature in {city} is {temp} degrees Celsius with {desc}.")
            else:
                self.speak(f"Sorry, I couldn't fetch the weather information for {city}.")
        except requests.RequestException as e:
            logger.error(f"Error fetching weather: {e}")
            self.speak("Sorry, I couldn't fetch the weather information.")

    def send_email(self, receiver_email: str, subject: str, message: str) -> None:
        """Send an email using configured credentials."""
        if not all([self.email, self.email_password]):
            self.speak("Email credentials are not configured.")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email, self.email_password)
                server.send_message(msg)
            
            self.speak("Email sent successfully.")
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            self.speak("Failed to send email.")

    def process_command(self, command: str) -> bool:
        """Process voice commands and execute appropriate actions."""
        try:
            if "hello" in command or "hi" in command:
                self.speak("Hello! How can I assist you today?")
            
            elif "time" in command:
                current_time = datetime.now().strftime("%I:%M %p")
                self.speak(f"The current time is {current_time}.")
            
            elif "date" in command:
                today = datetime.today().strftime("%B %d, %Y")
                self.speak(f"Today's date is {today}.")
            
            elif "news" in command:
                self.get_news()
            
            elif "weather" in command:
                self.speak("Which city's weather do you want to check?")
                city = self.recognize_speech()
                if city:
                    self.get_weather(city)
            
            elif "search" in command:
                search_query = re.sub(r"(search\s*)", "", command).strip()
                if search_query:
                    self.speak(f"Searching Google for {search_query}")
                    webbrowser.open(f"https://www.google.com/search?q={quote(search_query)}")
                else:
                    self.speak("Please specify what you'd like to search for.")
            
            elif "play" in command:
                video_query = command.replace("play", "").strip()
                self.speak(f"Playing {video_query} on YouTube")
                pywhatkit.playonyt(video_query)
            
            elif "exit" in command or "bye" in command:
                self.speak("Goodbye!")
                return False
            
            else:
                self.speak("I don't know that command yet.")
            
            return True
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            self.speak("Sorry, I encountered an error processing your command.")
            return True

    def run(self) -> None:
        """Main loop for the voice assistant."""
        self.speak("Hello! I'm your assistant. To exit, you can say 'bye' or 'exit'.")
        while True:
            command = self.recognize_speech()
            if command and not self.process_command(command):
                break

def main():
    """Main entry point for the voice assistant."""
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print("An unexpected error occurred. Please check the logs for details.")

if __name__ == "__main__":
    if __name__ == "__main__":
        main()

    