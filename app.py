from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simple mock data for testing first
AIRPORTS = {
    'JFK': 'New York (JFK)',
    'LAX': 'Los Angeles (LAX)',
    'LHR': 'London Heathrow (LHR)',
    'CDG': 'Paris Charles de Gaulle (CDG)',
    'DXB': 'Dubai (DXB)',
}

@app.route('/search-flights', methods=['POST'])
def search_flights():
    try:
        data = request.json
        from_airport = data.get('from_airport', '')
        to_airport = data.get('to_airport', '')
        date = data.get('date', '')
        
        # Return mock data first to test deployment
        mock_flights = [
            {
                'airline': 'Mock Airlines',
                'flight_number': 'MK123',
                'departure_time': f'{date} 08:00',
                'arrival_time': f'{date} 12:00',
                'duration': '4h 0m',
                'price': 299,
                'currency': 'USD',
                'stops': 0,
                'is_best': True
            },
            {
                'airline': 'Mock Airlines',
                'flight_number': 'MK456',
                'departure_time': f'{date} 14:00',
                'arrival_time': f'{date} 18:00',
                'duration': '4h 0m',
                'price': 249,
                'currency': 'USD',
                'stops': 1,
                'is_best': False
            }
        ]
        
        return jsonify({
            'success': True,
            'flights': mock_flights,
            'message': 'Mock data - Real flight search coming soon'
        })
        
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
