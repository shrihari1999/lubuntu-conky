import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.img_tiles import GoogleWTS
from cartopy.io import shapereader
import random, json, os
import matplotlib.image as mpimg
import matplotlib.patheffects as path_effects
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from datetime import datetime, timedelta
from io import BytesIO
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed

# Define the geographic coordinates of Tamil Nadu
southwest = (76.5, 11)  # (longitude, latitude) - lower left corner
northeast = (85, 15)  # (longitude, latitude) - upper right corner

# Create a tile source using a custom tile server
class CustomTileSource(GoogleWTS):
    def _image_url(self, tile):
        x, y, z = tile
        subdomain = random.choice('abc')
        
        # Get the current time
        now = datetime.now()
        # Round down to the nearest 10th minute
        rounded_time = now - timedelta(minutes=now.minute % 10, seconds=now.second, microseconds=now.microsecond)
        # Subtract 10 more mins as tile is not available in real time
        rounded_time = rounded_time - timedelta(minutes=10)

        # Convert to UTC
        utc_rounded_time = rounded_time - timedelta(hours=5, minutes=30)
        
        with open('weather.txt', 'w') as file:
            file.write(rounded_time.strftime("%I:%M %p"))
        return f"https://{subdomain}.sat.owm.io/maps/2.0/radar/{z}/{x}/{y}?appid=9de243494c0b295cca9337e1e96b00e2&day={utc_rounded_time.strftime('%Y-%m-%dT%H:%M')}"

# Create a Cartopy projection
projection = ccrs.PlateCarree()

# Desired size in pixels
desired_width_pixels = 685
desired_height_pixels = 345
dpi = 90

# Calculate size in inches
width_in_inches = desired_width_pixels / dpi
height_in_inches = desired_height_pixels / dpi

# Create a figure with the specified projection
fig = plt.figure(figsize=(width_in_inches, height_in_inches))
ax = plt.axes(projection=projection)

# Set the map extent to focus on Tamil Nadu
ax.set_extent([southwest[0], northeast[0], southwest[1], northeast[1]], crs=projection)

# Set aspect ratio to equal
ax.set_aspect('equal', adjustable='box')

# Add gridlines, coastlines, and any other necessary features for context
ax.add_feature(cfeature.LAND, facecolor='cyan')

# Load and plot city/district borders
shapefile_path = 'shape/in_district.shp'
reader = shapereader.Reader(shapefile_path)
shape_feature = cfeature.ShapelyFeature(reader.geometries(), projection, facecolor='none', edgecolor='#02c9c9', linewidth=1.5)
ax.add_feature(shape_feature)

ax.add_feature(cfeature.STATES, edgecolor='#dc143c', linewidth=1.5)

# Initialize the tile source with your custom server
tiler = CustomTileSource(desired_tile_form='RGBA')
tiler.request = {'zoom_level': 7}

# Add the radar tile overlay from the server with transparency
ax.add_image(tiler, 7, zorder=2)

# Remove the axes and any extra borders
ax.set_axis_off()

plt.tight_layout()

# Extract cities data
with open('cities.json', 'r') as file:
    data = json.load(file)

session = FuturesSession()

weather_futures = []
for feature in data:
    coordinates = feature['coordinates']
    city = feature['city']

    future = session.get(f"https://api.openweathermap.org/data/2.5/weather?lat={coordinates[1]}&lon={coordinates[0]}&units=metric&appid=f4f5ed488ce0ad096a0e29394c04be9a")
    future.custom_data = {'coordinates': coordinates, 'city': city} 
    weather_futures.append(future)

icon_futures = []
for weather_future in as_completed(weather_futures):
    response = weather_future.result().json()  # Get the result of the future
    coordinates = weather_future.custom_data['coordinates']
    city = weather_future.custom_data['city']

    if 'main' in response and 'weather' in response:
        temp = round(response['main']['temp'])
        icon_code = response['weather'][0]['icon']

        # Prepare the API call for the icon asynchronously
        icon_future = session.get(f"https://openweathermap.org/img/wn/{icon_code}.png")
        icon_future.custom_data = {'coordinates': coordinates, 'temp': temp, 'city': city}  # Store custom data
        icon_futures.append(icon_future)

# Now process the icon futures as they complete
for icon_future in as_completed(icon_futures):
    icon_response = icon_future.result()
    coordinates = icon_future.custom_data['coordinates']
    temp = icon_future.custom_data['temp']
    city = icon_future.custom_data['city']

    img = mpimg.imread(BytesIO(icon_response.content), format='png')

    # Create an offset image and add it to the plot
    imagebox = OffsetImage(img, zoom=0.6)  # Adjust zoom as needed
    
    icon_offset = 0.15 if city == 'Ooty' else 0
    ab = AnnotationBbox(imagebox, (coordinates[0] + icon_offset, coordinates[1]), frameon=False)
    ax.add_artist(ab)

    # Place the text on the plot
    text_offset = icon_offset + 0.2
    ax.text(coordinates[0] + text_offset, coordinates[1], f"{temp}°C {city}",
        fontsize=9.4, ha='left', va='center', color='white',
        path_effects=[path_effects.withStroke(linewidth=1.5, foreground='black')]
    )

plt.savefig('weather.png', transparent=True, bbox_inches='tight', dpi=dpi, pad_inches=0)

os.system('convert weather.png -background transparent -flatten weather.png')