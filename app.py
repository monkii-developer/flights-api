from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import time
import random

app = Flask(__name__)
CORS(app)

AIRPORTS = {
    'JFK': 'New York (JFK)',
    'LAX': 'Los Angeles (LAX)',
    'LHR': 'London Heathrow (LHR)',
    'CDG': 'Paris Charles de Gaulle (CDG)',
    'DXB': 'Dubai (DXB)',
    'NRT': 'Tokyo Narita (NRT)',
    'SIN': 'Singapore Changi (SIN)',
    'HKG': 'Hong Kong International (HKG)',
    'SYD': 'Sydney Kingsford Smith (SYD)',
    'FRA': 'Frankfurt am Main (FRA)',
    'AMS': 'Amsterdam Schiphol (AMS)',
    'ICN': 'Seoul Incheon (ICN)',
    'PEK': 'Beijing Capital (PEK)',
    'DEL': 'Delhi Indira Gandhi (DEL)',
    'BOM': 'Mumbai Chhatrapati Shivaji (BOM)',
    'SFO': 'San Francisco International (SFO)',
    'ORD': 'Chicago O\'Hare (ORD)',
    'DFW': 'Dallas/Fort Worth (DFW)',
    'DEN': 'Denver International (DEN)',
    'SEA': 'Seattle-Tacoma (SEA)',
    'MIA': 'Miami International (MIA)',
    'BOS': 'Boston Logan (BOS)',
    'ATL': 'Atlanta Hartsfield-Jackson (ATL)',
    'YYZ': 'Toronto Pearson (YYZ)',
    'MEX': 'Mexico City International (MEX)',
}

# Simple cache to avoid repeated requests
flight_cache = {}
cache_timeout = 300  # 5 minutes

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Flight API is running!',
        'endpoints': {
            'health': '/health',
            'search_flights': '/search-flights (POST)',
            'search_airports': '/airports/search?q=JFK (GET)'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Flight API is running!'})

@app.route('/search-flights', methods=['POST'])
def search_flights():
    try:
        data = request.json
        from_airport = data.get('from_airport', '').strip().upper()
        to_airport = data.get('to_airport', '').strip().upper()
        date = data.get('date', '')
        trip_type = data.get('trip', 'one-way')
        return_date = data.get('return_date')
        adults = int(data.get('adults', 1))
        
        # Create cache key
        cache_key = f"{from_airport}_{to_airport}_{date}_{trip_type}_{return_date}_{adults}"
        
        # Check cache
        if cache_key in flight_cache:
            cache_time, cached_data = flight_cache[cache_key]
            if time.time() - cache_time < cache_timeout:
                return jsonify(cached_data)
        
        # For now, return enhanced mock data with more realistic prices
        # In production, you could replace this with a real flight API like:
        # - Amadeus API
        # - Skyscanner API  
        # - Travelpayouts API
        # - Google Flights (via serpapi.com)
        
        import random
        random.seed(f"{from_airport}{to_airport}{date}")
        
        # Generate realistic mock data based on route
        base_price = 200
        if from_airport in ['JFK', 'LAX', 'SFO'] and to_airport in ['LHR', 'CDG']:
            base_price = 800  # Transatlantic
        elif from_airport in ['JFK', 'LAX'] and to_airport in ['NRT', 'HKG', 'SIN']:
            base_price = 1200  # Transpacific
        elif from_airport in ['JFK', 'LHR'] and to_airport in ['DXB']:
            base_price = 1000  # Long haul
        else:
            base_price = 200  # Domestic/Regional
        
        airlines = ['Delta', 'United', 'American', 'British Airways', 'Emirates', 'Singapore Airlines', 'Qatar Airways']
        
        flights = []
        for i in range(5):
            airline = random.choice(airlines)
            price_variation = random.randint(-50, 150)
            price = max(base_price + price_variation, 100)
            
            hour = random.randint(6, 20)
            duration = random.randint(2, 8)
            arrival_hour = (hour + duration) % 24
            
            flights.append({
                'airline': airline,
                'flight_number': f"{airline[:2].upper()}{random.randint(100, 999)}",
                'departure_time': f"{date} {hour:02d}:00",
                'arrival_time': f"{date} {arrival_hour:02d}:00",
                'duration': f"{duration}h 0m",
                'price': price,
                'currency': 'USD',
                'stops': random.randint(0, 2),
                'is_best': i == 0
            })
        
        # Sort by price
        flights.sort(key=lambda x: x['price'])
        flights[0]['is_best'] = True
        
        response_data = {
            'success': True,
            'flights': flights,
            'total_flights': len(flights),
            'message': 'Demo mode - Real API coming soon'
        }
        
        # Cache the response
        flight_cache[cache_key] = (time.time(), response_data)
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/airports/search', methods=['GET'])
def search_airports():
    query = request.args.get('q', '').lower()
    results = []
    for code, name in AIRPORTS.items():
        if query in code.lower() or query in name.lower():
            results.append({
                'code': code,
                'name': name,
                'city': name.split('(')[0].strip(),
            })
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
