from flask import Flask, request, jsonify
from pytrends.request import TrendReq
from flask_caching import Cache  # Import Flask-Caching
import logging

app = Flask(__name__)

# Configure Flask-Caching (Simple in-memory cache)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})  # 5-minute cache

# Set up Google Trends API
pytrends = TrendReq(hl='en-US', tz=360)

# Set up basic logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    app.logger.info('Home endpoint accessed')
    return "Google Trends API is running"

# Cache the result of trends queries for 5 minutes (300 seconds)
@cache.cached(timeout=300, query_string=True)
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

        if trends_data.empty:
            app.logger.warning(f"No data found for query: {search_query}")
            return jsonify({'error': 'No data found for this query'}), 404

        # Convert trends data to a dictionary and return as JSON
        trends_dict = trends_data.reset_index().to_dict(orient='records')
        return jsonify({'search_query': search_query, 'trends': trends_dict})

    except Exception as e:
        app.logger.error(f"Error fetching trends data for '{search_query}': {str(e)}")
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
