from flask import Flask, request, jsonify
from flask_cors import CORS
from fast_flights import FlightData, Passengers, get_flights

app = Flask(__name__)
CORS(app)

# Airport list for search
AIRPORTS = {
    'JFK': 'New York (JFK)',
    'LAX': 'Los Angeles (LAX)',
    'LHR': 'London Heathrow (LHR)',
    'CDG': 'Paris Charles de Gaulle (CDG)',
    'DXB': 'Dubai (DXB)',
    'NRT': 'Tokyo Narita (NRT)',
    'SIN': 'Singapore (SIN)',
    'HKG': 'Hong Kong (HKG)',
    'SYD': 'Sydney (SYD)',
    'FRA': 'Frankfurt (FRA)',
    'AMS': 'Amsterdam (AMS)',
    'ICN': 'Seoul Incheon (ICN)',
    'PEK': 'Beijing (PEK)',
    'DEL': 'Delhi (DEL)',
    'BOM': 'Mumbai (BOM)',
}

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
        seat = data.get('seat', 'economy')
        
        if not from_airport or not to_airport or not date:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        flight_data = [FlightData(date=date, from_airport=from_airport, to_airport=to_airport)]
        
        if trip_type == 'round-trip' and return_date:
            flight_data.append(FlightData(date=return_date, from_airport=to_airport, to_airport=from_airport))
        
        result = get_flights(
            flight_data=flight_data,
            trip=trip_type,
            seat=seat,
            passengers=Passengers(adults=adults, children=0, infants_in_seat=0, infants_on_lap=0),
            fetch_mode="fallback"
        )
        
        flights = []
        for flight in result.flights:
            flights.append({
                'airline': flight.name.split()[0] if flight.name else 'Unknown',
                'flight_number': flight.name if flight.name else 'N/A',
                'departure_time': flight.departure,
                'arrival_time': flight.arrival,
                'duration': flight.duration,
                'price': float(flight.price) if flight.price else 0,
                'currency': 'USD',
                'stops': flight.stops,
                'is_best': flight.is_best,
                'arrival_time_ahead': flight.arrival_time_ahead,
            })
        
        return jsonify({'success': True, 'flights': flights})
        
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

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Flight API is running!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
