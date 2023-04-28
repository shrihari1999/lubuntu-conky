import os, requests
from datetime import datetime
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup

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
response = requests.get('https://wttr.in/Chennai?format=j1').json()
hourly_condition = response['weather'][0]['hourly'][int(hour/3)]
temperature = hourly_condition['tempC']
wind_speed = float(hourly_condition['windspeedKmph'])
hourly_weather_desc = hourly_condition['weatherDesc'][0]['value']
current_condition = response['current_condition'][0]
current_weather_desc = current_condition['weatherDesc'][0]['value']

text += f"The weather in Chennai is {temperature} degrees, {hourly_weather_desc}"
if hourly_weather_desc.lower() != current_weather_desc.lower():
    text += f", {current_weather_desc}"
text += '.'

if wind_speed > 50:
    text += f" Warning! High wind speeds detected upto {wind_speed} kilometers per hour. A High Threat to Life and Property from High Wind is expected."

# speak
tts = gTTS(text, lang='en', tld='ca')
tts.save('voice.mp3')
audio = AudioSegment.from_mp3('voice.mp3')
fast_audio = speedup(audio, 1.2)
play(fast_audio)
os.remove('voice.mp3')
