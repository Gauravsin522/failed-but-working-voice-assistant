from http.server import executable
from tarfile import data_filter
from click import command
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
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import openai




# Context memory for storing previous interactions
context_memory = {}
user_data_file="user_data.json"




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

    

# Set up your OpenAI API Key
openai.api_key = "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"

def chat_with_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

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

command = recognize_speech()  # Ensure it's called
if "chat mode" in command or "talk to me" in command:
    speak("Sure! What would you like to talk about?")
    while True:
        user_input = recognize_speech()  # Ensure this is called too
        if "exit chat" in user_input or "stop talking" in user_input:
            speak("Exiting chat mode.")
            break
        response = chat_with_gpt(user_input)
        speak(response)


    
def personalize_greeting():
    user_data=load_user_data()
    name=user_data.get("name","User")
    
    current_hour=datetime.datetime.now().hour
    if current_hour < 12:
        greeting="Good Morning"
    elif 12 <= current_hour < 18:
        greeting="Good Afternoon"
    else:
        greeting="Good Evening"
        
    return f"{greeting}, {name}!How can I assist you today?"
def load_user_data():
    try:
        with open(user_data_file, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {}
    
def save_user_data(data):
    with open(user_data_file, 'w') as file:
        json.dump(data, file,indent=4)
    
def send_email(receiver_email, subject,message):
    sender_email = "gauravfuunn@gmail.com"
    sender_password = "*******"  # Replace with your email password
    
    msg=MIMEMultipart()
    msg['From']=sender_email
    msg['To']=receiver_email
    msg['Subject']=subject
    msg.attach(MIMEText(message,'plain'))
    
    try:
        server=smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(sender_email,sender_password)
        server.send_message(msg)
        server.quit()
        speak("Email sent successfully.")
        
    except Exception as e:
        speak("Failed to send email.")
        print(f"Error: {e}")
        
def email_assistant():
    speak("Please tell me the recipient's email address.")
    recipient_email = recognize_speech()
    if recipient_email:
        receiver_email = recipient_email.replace(" ", "")+"@gmail.com"  # Assuming Gmail for simplicity
        speak("What is the subject of the email?")
        subject = recognize_speech()
        
        speak("What is the message you want to send?")
        message = recognize_speech()
        if subject and message:
            send_email(receiver_email, subject, message)
            

def get_news():
    api_key = "aee28e8736ad4aab896c56fb2f3593d8"  # Replace with your NewsAPI key
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
    api_key = "90e187b1983f4d3e977103649252403"  # Replace with your OpenWeatherMap API key
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
        
def google_search(query):
    speak(f"Searching Google for {query}")
    
    driver = webdriver.Edge(executable_path="MicrosoftWebDriver.exe")
    driver.get("https://www.google.com")
    
    search_box = driver.find_element_by_name('name',"q")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5) 
    speak("Here are the search results.")

if "google search" in command:
    query = command.replace("google search", "").strip()
    google_search(query)
elif "open" in command:
    site = command.replace("open", "").strip().lower()
    web_links = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "linkedin": "https://www.linkedin.com",
        "github": "https://github.com",
        "twitter": "https://twitter.com",
        "gmail": "https://mail.google.com"
    }
    if site in web_links:
        speak(f"Opening {site}")
        os.system(f'start msedge {web_links[site]}')
    else:
        speak(f"Sorry, I don't have a shortcut for {site}, but I can search for it.")
        os.system(f'start msedge "https://www.google.com/search?q={quote(site)}"')
elif "search" in command:
    search_query = command.replace("search", "").strip()
    if search_query:
        speak(f"Searching Google for {search_query}")
        os.system(f'start msedge "https://www.google.com/search?q={quote(search_query)}"')
    else:
        speak("Please specify what you'd like to search for.")
elif "find jobs" in command:
    job_role = command.replace("find jobs", "").strip()
    if job_role:
        speak(f"Searching LinkedIn for {job_role} jobs")
        os.system(f'start msedge "https://www.linkedin.com/jobs/search/?keywords={quote(job_role)}"')
    else:
        speak("Please specify a job title.")
elif "search youtube for" in command:
    yt_query = command.replace("search youtube for", "").strip()
    speak(f"Searching YouTube for {yt_query}")
    os.system(f'start msedge "https://www.youtube.com/results?search_query={quote(yt_query)}"')
 


HOME_ASSISTANT_URL = "http://your-home-assistant-ip:8123/api/services/light/turn_on"
HEADERS = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN",
    "Content-Type": "application/json"
}

if "turn on the light" in command:
    speak("Turning on the light")
    data = {"entity_id": "light.your_light_id"}
    requests.post(HOME_ASSISTANT_URL, headers=HEADERS, json=data)


def open_system_app(app_name):
    try:
        if app_name == "calculator":
            os.startfile("C:\\Windows\\System32\\calc.exe")
        elif app_name == "file explorer":
            os.system("explorer")
        elif app_name == "notepad":
            os.system("notepad.exe")
        elif app_name == "command prompt":
            os.system("cmd.exe")
        elif app_name == "settings":
            os.system("ms-settings:")
        elif app_name == "control panel":
            os.system("control.exe")
        elif app_name == "chrome":
            os.system("chrome.exe")  
            speak("Sorry, I don't know how to open that application.")
    except Exception as e:
        speak(f"Failed to open {app_name}: {e}")

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
        
    elif "open" in command:
        if "google" in command:
            speak("Opening Google")
            webbrowser.open("https://www.google.com")
        elif "youtube" in command:
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")
        else:
            app_name = re.sub(r"(open\s*)", "", command).strip()
            open_system_app(app_name)
            
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
            
    elif "volume up" in command or "increase volume" in command:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current_volume = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(min(current_volume + 0.1, 1.0), None)
        speak("Volume increased.")
        
    elif "volume down" in command or "decrease volume" in command:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current_volume = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(max(current_volume - 0.1, 0.0), None)
        speak("Volume decreased.")
        
    elif "mute" in command:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(1, None)
        speak("Muted.")
        
    elif "remind me" in command:
        reminder = command.replace("remind me", "").strip()
        context_memory["last_reminder"] = reminder
        speak(f"Reminder set for {reminder}.")
        
    elif "what is my reminder" in command:
        if "last_reminder" in context_memory:
            speak(f"Your last reminder was: {context_memory['last_reminder']}")
        else:
            speak("You don't have any reminders set.")
            
    elif "who am i" in command:
        if "user_name" in context_memory:
            speak(f"Your name is {context_memory['user_name']}.")
        else:
            speak("I don't know your name yet. Please tell me your name.")
            user_name = recognize_speech()
            if user_name:
                context_memory["user_name"] = user_name
                speak(f"Got it! Your name is {user_name}.")
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