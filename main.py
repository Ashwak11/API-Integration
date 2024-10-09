import sqlite3
import requests
from fastapi import FastAPI, HTTPException # type: ignore
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()

# Database setup
def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS combined_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT,
                    crypto_id TEXT,
                    breed TEXT,
                    temperature REAL,
                    current_price REAL,
                    image_url TEXT,
                    timestamp TEXT
                 )''')
    conn.commit()
    conn.close()

init_db()

# API keys
WEATHER_API_KEY = '3ece62b5adbde95aa96074250a052729'  # Replace with your actual OpenWeatherMap API key
DOG_API_KEY = 'live_z3iQszuddDzwzBhutcdCY6kZcesOUKutltf7tGYLPwogNMIxQy7Y2FUiDf5Gfj0J'  # Replace with your actual Dog API key

# Data Extraction
def fetch_weather_data(city_name):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "temperature": data['main']['temp'],
            "description": data['weather'][0]['description']
        }
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=400, detail=f"HTTP error occurred: {http_err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {err}")

def fetch_crypto_data(crypto_id):
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "current_price": data[crypto_id]['usd']
        }
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=400, detail=f"HTTP error occurred: {http_err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {err}")

def fetch_dog_data(breed):
    url = 'https://api.thedogapi.com/v1/breeds'
    headers = {'x-api-key': DOG_API_KEY}
    response = requests.get(url, headers=headers)
    breeds = response.json()
    
    breed_info = next((b for b in breeds if breed.lower() in b['name'].lower()), None)
    if breed_info:
        breed_id = breed_info['id']
        image_response = requests.get(f'https://api.thedogapi.com/v1/images/search?breed_id={breed_id}', headers=headers)
        image_url = image_response.json()[0]['url']
        return {
            "image_url": image_url,
            "group": breed_info.get('breed_group', 'N/A'),
            "life_span": breed_info.get('life_span', 'N/A'),
            "temperament": breed_info.get('temperament', 'N/A')
        }
    else:
        raise HTTPException(status_code=404, detail="Breed not found")

# Combined data endpoint
@app.post("/combined-data")
def get_combined_data(city: str, crypto_id: str, breed: str):
    # Fetch data
    weather = fetch_weather_data(city)
    crypto = fetch_crypto_data(crypto_id)
    dog = fetch_dog_data(breed)
    
    # Combine data
    combined_data = {
        "city": city,
        "crypto_id": crypto_id,
        "breed": breed,
        "temperature": weather['temperature'],
        "current_price": crypto['current_price'],
        "image_url": dog['image_url'],
        "timestamp": datetime.now().isoformat()
    }
    
    # Store in database
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''INSERT INTO combined_data (city, crypto_id, breed, temperature, current_price, image_url, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', 
              (city, crypto_id, breed, weather['temperature'], crypto['current_price'], dog['image_url'], combined_data['timestamp']))
    conn.commit()
    conn.close()
    
    return combined_data

# Retrieve historical data
@app.get("/combined-data/history")
def get_history(start_date: str = None, end_date: str = None):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    query = "SELECT * FROM combined_data"
    params = []
    
    if start_date and end_date:
        query += " WHERE timestamp BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    history = [
        {
            "id": row[0],
            "city": row[1],
            "crypto_id": row[2],
            "breed": row[3],
            "temperature": row[4],
            "current_price": row[5],
            "image_url": row[6],
            "timestamp": row[7]
        } for row in rows
    ]
    
    return history

# Weather endpoint
@app.get("/weather")
def get_weather(city: str):
    weather = fetch_weather_data(city)
    return weather

# Cryptocurrency endpoint
@app.get("/crypto")
def get_crypto(crypto_id: str):
    crypto = fetch_crypto_data(crypto_id)
    return crypto

# Dog endpoint
@app.get("/dogs")
def get_dog(breed: str):
    dog = fetch_dog_data(breed)
    return dog

if __name__ == '__main__':
    init_db()  # Ensure the database is initialized when running the script
    import uvicorn # type: ignore
    uvicorn.run(app, host="127.0.0.1", port=8001)
