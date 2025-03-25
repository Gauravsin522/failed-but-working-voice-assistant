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
import os
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

# Context memory for storing previous interactions
context_memory = {}
user_data_file = "user_data.json"

# Initialize the text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Female voice
engine.setProperty('rate', 150)  # Speed
engine.setProperty('volume', 1.0)  # Volume

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Initialize the speech recognizer
recognizer = sr.Recognizer()

def recognize_speech():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand that. Please try again.")
        except sr.RequestError:
            speak("Network error. Please check your internet connection.")

def personalize_greeting():
    user_data = load_user_data()
    name = user_data.get("name", "User")
    
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif 12 <= current_hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
        
    return f"{greeting}, {name}! How can I assist you today?"

def load_user_data():
    try:
        with open(user_data_file, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open(user_data_file, 'w') as file:
        json.dump(data, file, indent=4)

def send_email(receiver_email, subject, message):
    sender_email = "your_email@gmail.com"
    sender_password = "your_password"  # Replace with your email password
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        speak("Email sent successfully.")
    except Exception as e:
        speak("Failed to send email.")
        print(f"Error: {e}")

def get_news():
    api_key = "your_newsapi_key"  # Replace with your NewsAPI key
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
    response = requests.get(url).json()

    if "articles" in response:
        articles = response["articles"][:3]  # Fetch top 3 news articles
        news = [article["title"] for article in articles]
        for i, headline in enumerate(news, 1):
            speak(f"News {i}: {headline}")
    else:
        speak("Sorry, I couldn't fetch the news at the moment.")

def get_weather(city="Delhi"):
    api_key = "your_openweathermap_key"  # Replace with your OpenWeatherMap API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={quote(city)}&appid={api_key}&units=metric"
    response = requests.get(url).json()

    if response.get("cod") == 200:
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        speak(f"The current temperature in {city} is {temp} degrees Celsius with {desc}.")
    else:
        speak(f"Sorry, I couldn't fetch the weather information for {city}.")

def set_reminder(task, delay):
    try:
        delay = int(delay)
        speak(f"Setting a reminder for {task} in {delay} seconds.")
        time.sleep(delay)
        notification.notify(
            title="Reminder",
            message=task,
            timeout=10
        )
        speak(f"Reminder: {task}")
    except ValueError:
        speak("The delay must be a number. Please try again.")

def process_command(command):
    global context_memory
    if "hello" in command:
        speak("Hello! How can I assist you today?")
        
    elif "time" in command:
        current_time = datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}.")
        
    elif "date" in command:
        today = datetime.today().strftime("%B %d, %Y")
        speak(f"Today's date is {today}.")
        
    elif "exit" in command or "bye" in command:
        speak("Goodbye!")
        return False
        
    elif "search" in command:
        search_query = re.sub(r"(search\s*)", "", command).strip()
        if search_query:
            speak(f"Searching Google for {search_query}")
            webbrowser.open(f"https://www.google.com/search?q={quote(search_query)}")
        else:
            speak("Please specify what you'd like to search for.")
            
    elif "play" in command:
        video_query = command.replace("play", "").strip()
        speak(f"Playing {video_query} on YouTube")
        pywhatkit.playonyt(video_query)
        
    elif "news" in command:
        speak("Fetching the latest news for you.")
        get_news()
        
    elif "weather" in command:
        speak("Which city's weather do you want to check?")
        city = recognize_speech()  # Capture the city name
        if city:
            get_weather(city)
            
    elif "reminder" in command:
        speak("What should I remind you about?")
        task = recognize_speech()
        speak("In how many seconds?")
        delay = recognize_speech()
        if task and delay:
            set_reminder(task, delay)
            
    else:
        speak("I don't know that command yet.")
    return True

def main():
    speak("Hello! I'm your assistant. To exit, you can say 'bye' or 'exit'.")
    while True:
        command = recognize_speech()
        if command and not process_command(command):
            break

if __name__ == "__main__":
    main()