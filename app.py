from flask import Flask, request, jsonify
import requests
from cachetools import TTLCache
from datetime import datetime

app = Flask(__name__)

# Cache weather data for 10 minutes to reduce API calls
cache = TTLCache(maxsize=100, ttl=600)

# Replace 'YOUR_API_KEY' with your OpenWeatherMap API key
# Get one at: https://openweathermap.org/api
API_KEY = 'effb5a1930f093a3bd1b55b41df7a0e6'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/weather')
def get_weather():
    city = request.args.get('city', '').strip()
    
    if not city:
        return jsonify({'error': 'City parameter is required'}), 400

    # Check cache first
    cache_key = city.lower()
    if cache_key in cache:
        return jsonify(cache[cache_key])

    try:
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric'  # For Celsius
        }
        response = requests.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()

        if response.status_code != 200:
            return jsonify({'error': data.get('message', 'City not found').capitalize()}), 404

        weather_data = {
            'city': data['name'],
            'temperature': round(data['main']['temp']),
            'feels_like': round(data['main']['feels_like']),
            'description': data['weather'][0]['description'].capitalize(),
            'humidity': data['main']['humidity'],
            'wind': data['wind']['speed'],
            'icon': data['weather'][0]['icon'],
            'timestamp': datetime.utcnow().isoformat()
        }

        # Store in cache
        cache[cache_key] = weather_data
        return jsonify(weather_data)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch weather data: {str(e)}'}), 500
    except KeyError:
        return jsonify({'error': 'Invalid response from weather service'}), 500

if __name__ == '__main__':
    app.run(debug=True) 