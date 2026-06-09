from flask import Flask, request, jsonify
from flask_cors import CORS
from fast_flights import FlightData, Passengers, get_flights
import traceback

app = Flask(__name__)
CORS(app)

# Expanded airport list for better search
AIRPORTS = {
    'JFK': 'New York John F Kennedy (JFK)',
    'LAX': 'Los Angeles International (LAX)',
    'LHR': 'London Heathrow (LHR)',
    'CDG': 'Paris Charles de Gaulle (CDG)',
    'DXB': 'Dubai International (DXB)',
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
        print("Received request:", data)
        
        from_airport = data.get('from_airport', '').strip().upper()
        to_airport = data.get('to_airport', '').strip().upper()
        date = data.get('date', '')
        trip_type = data.get('trip', 'one-way')
        return_date = data.get('return_date')
        adults = int(data.get('adults', 1))
        seat = data.get('seat', 'economy')
        
        # Validate inputs
        if not from_airport or not to_airport or not date:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Create flight data list
        flight_data = [
            FlightData(
                date=date,
                from_airport=from_airport,
                to_airport=to_airport,
            )
        ]
        
        # Add return flight for round trip
        if trip_type == 'round-trip' and return_date:
            flight_data.append(
                FlightData(
                    date=return_date,
                    from_airport=to_airport,
                    to_airport=from_airport,
                )
            )
        
        print(f"Searching flights from {from_airport} to {to_airport} on {date}")
        
        # Get real flights from Google
        result = get_flights(
            flight_data=flight_data,
            trip=trip_type,
            seat=seat,
            passengers=Passengers(adults=adults, children=0, infants_in_seat=0, infants_on_lap=0),
            fetch_mode="fallback"  # This handles EU consent pages
        )
        
        # Format the results
        flights = []
        for flight in result.flights:
            flights.append({
                'airline': flight.name.split()[0] if flight.name else 'Unknown',
                'flight_number': flight.name if flight.name else 'N/A',
                'departure_time': flight.departure,
                'arrival_time': flight.arrival,
                'arrival_time_ahead': flight.arrival_time_ahead,
                'duration': flight.duration,
                'price': float(flight.price) if flight.price else 0,
                'currency': 'USD',
                'stops': flight.stops,
                'delay': flight.delay,
                'is_best': flight.is_best
            })
        
        # Format response for round trips
        if trip_type == 'round-trip' and len(flights) >= 2:
            # Separate outbound and return flights
            outbound = flights[0::2]  # Every other flight starting at index 0
            returning = flights[1::2]  # Every other flight starting at index 1
            
            formatted_flights = []
            for i in range(min(len(outbound), len(returning))):
                formatted_flights.append({
                    'outbound': outbound[i],
                    'return': returning[i],
                    'total_price': outbound[i]['price'] + returning[i]['price']
                })
            flights = formatted_flights
        
        return jsonify({
            'success': True,
            'flights': flights,
            'current_price': result.current_price,
            'total_flights': len(flights)
        })
        
    except Exception as e:
        print(f"Error: {traceback.format_exc()}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'message': 'Failed to search flights. Please try again.'
        }), 500

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
