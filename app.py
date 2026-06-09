from flask import Flask, request, jsonify
from flask_cors import CORS
from fast_flights import FlightData, Passengers, get_flights

app = Flask(__name__)
CORS(app)

@app.route('/search-flights', methods=['POST'])
def search_flights():
    try:
        data = request.json
        from_airport = data.get('from_airport', '').strip().upper()
        to_airport = data.get('to_airport', '').strip().upper()
        date = data.get('date', '')
        adults = int(data.get('adults', 1))

        # Create the flight data structure exactly as the library expects
        flight_data = [
            FlightData(
                date=date,
                from_airport=from_airport,
                to_airport=to_airport,
            )
        ]

        # Call the real scraper
        result = get_flights(
            flight_data=flight_data,
            trip="one-way",
            seat="economy",
            passengers=Passengers(adults=adults),
            fetch_mode="fallback"   # This uses an external service, not local Playwright
        )

        # Parse the result
        flights = []
        for flight in result.flights:
            flights.append({
                'airline': flight.name.split()[0] if flight.name else 'Unknown',
                'flight_number': flight.name,
                'departure_time': flight.departure,
                'arrival_time': flight.arrival,
                'duration': flight.duration,
                'price': float(flight.price) if flight.price else 0,
                'stops': flight.stops,
                'is_best': flight.is_best
            })

        return jsonify({'success': True, 'flights': flights})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
