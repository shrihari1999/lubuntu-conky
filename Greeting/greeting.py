import os, requests, time
from datetime import datetime
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup

time.sleep(10)

text = ''

# greeting
now = datetime.now()
hour = now.hour
time_of_day = 'morning' if hour < 12 else 'afternoon' if hour < 16 else 'evening'

text += f"Good {time_of_day}!"

# time
time = now.strftime('%I:%M %p')
text += f"It's {time},"

# weather
coordinates = [80.2785, 13.0878]

response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={coordinates[1]}&lon={coordinates[0]}&units=metric&appid=f4f5ed488ce0ad096a0e29394c04be9a").json()

temperature = round(response['main']['temp'])
wind_speed = response['wind']['speed'] * 3.6 # convert to kmph
hourly_weather_desc = response['weather'][0]['description']

text += f"The weather in Chennai is {temperature} degrees... {hourly_weather_desc}."

if wind_speed > 50:
    text += f" Warning! High wind speeds detected upto {wind_speed} kilometers per hour. A High Threat to Life and Property from High Wind is expected."

# speak
tts = gTTS(text, lang='en', tld='ca')
tts.save('voice.mp3')
audio = AudioSegment.from_mp3('voice.mp3')
os.remove('voice.mp3')
fast_audio = speedup(audio, 1.2)
play(fast_audio)
