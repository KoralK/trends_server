import logging
from flask import Flask

app = Flask(__name__)

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO)

# Example log entries
@app.route('/')
def home():
    app.logger.info('Home endpoint accessed')
    return "Google Trends API is running"

@app.route('/trends', methods=['GET'])
def get_trends():
    search_query = request.args.get('q')

    print(f"Search query: {search_query}")  # This will print to Render logs

    if not search_query:
        print("Error: No search query provided")
        return jsonify({'error': 'Please provide a search query (q)'}), 400

    # Rest of your logic

    try:
        # Log the search query
        app.logger.info(f"Fetching trends data for: {search_query}")
        
        # Existing logic to fetch trends data...
        return jsonify({'success': 'Trends data fetched'})

    except Exception as e:
        # Log any exceptions or errors
        app.logger.error(f"Error fetching trends data: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
