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

    if not search_query:
        app.logger.error("No search query provided")
        return jsonify({'error': 'Please provide a search query (q)'}), 400

    try:
        app.logger.info(f"Fetching trends data for: {search_query}")
        pytrends.build_payload([search_query], cat=0, timeframe='now 7-d', geo='US', gprop='')

        # Get interest over time for the search query
        trends_data = pytrends.interest_over_time()

        # Check if trends data is empty
        if trends_data.empty:
            app.logger.warning(f"No data found for query: {search_query}")
            return jsonify({'error': 'No data found for this query'}), 404

        # Convert the trends data to a dictionary and send as JSON response
        trends_dict = trends_data.reset_index().to_dict(orient='records')
        return jsonify({'search_query': search_query, 'trends': trends_dict})

    except Exception as e:
        # Log any exception for debugging
        app.logger.error(f"Error fetching trends data: {str(e)}")
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
