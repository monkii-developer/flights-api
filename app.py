from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import traceback

app = Flask(__name__)
CORS(app)

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
        adults = int(data.get('adults', 1))
        
        # Try the correct import paths for fast-flights
        try:
            # Method 1: Try the newer v3 API
            from fast_flights import FlightQuery, Passengers, get_flights, create_query
            
            query = create_query(
                flights=[
                    FlightQuery(
                        date=date,
                        from_airport=from_airport,
                        to_airport=to_airport,
                    ),
                ],
                seat="economy",
                trip="one-way",
                passengers=Passengers(adults=adults),
            )
            result = get_flights(query)
            
        except ImportError:
            try:
                # Method 2: Try the older v2 API
                from fast_flights import FlightData, Passengers, get_flights
                
                from fast_flights import create_filter
                flight_data = [
                    FlightData(
                        date=date,
                        from_airport=from_airport,
                        to_airport=to_airport,
                    )
                ]
                
                flight_filter = create_filter(
                    flight_data=flight_data,
                    trip="one-way",
                    seat="economy",
                    passengers=Passengers(adults=adults),
                )
                result = get_flights(flight_filter)
                
            except ImportError:
                # If both fail, return mock data
                return jsonify({
                    'success': True,
                    'flights': [
                        {
                            'airline': 'Demo Airlines',
                            'flight_number': 'FL123',
                            'departure_time': f'{date} 08:00',
                            'arrival_time': f'{date} 12:00',
                            'duration': '4h 0m',
                            'price': 299,
                            'currency': 'USD',
                            'stops': 0,
                            'is_best': True
                        }
                    ],
                    'message': 'Fast-flights import failed, using demo data'
                })
        
        # Parse the result (works for both API versions)
        flights = []
        if hasattr(result, 'flights'):
            for flight in result.flights:
                flights.append({
                    'airline': getattr(flight, 'airline', 'Unknown'),
                    'flight_number': getattr(flight, 'flight_number', 'N/A'),
                    'departure_time': getattr(flight, 'departure_time', 'N/A'),
                    'arrival_time': getattr(flight, 'arrival_time', 'N/A'),
                    'duration': getattr(flight, 'duration', 'N/A'),
                    'price': float(getattr(flight, 'price', 0)),
                    'currency': 'USD',
                    'stops': getattr(flight, 'stops', 0),
                    'is_best': getattr(flight, 'is_best', False)
                })
        
        return jsonify({'success': True, 'flights': flights})
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500

@app.route('/airports/search', methods=['GET'])
def search_airports():
    query = request.args.get('q', '').lower()
    airports = {
        'JFK': 'New York John F Kennedy',
        'LAX': 'Los Angeles International',
        'LHR': 'London Heathrow',
        'CDG': 'Paris Charles de Gaulle',
        'DXB': 'Dubai International',
        'NRT': 'Tokyo Narita',
        'SIN': 'Singapore Changi',
        'HKG': 'Hong Kong International',
        'SYD': 'Sydney Kingsford Smith',
        'FRA': 'Frankfurt am Main',
        'AMS': 'Amsterdam Schiphol',
    }
    results = []
    for code, name in airports.items():
        if query in code.lower() or query in name.lower():
            results.append({
                'code': code,
                'name': name,
                'city': name.split()[0]
            })
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
