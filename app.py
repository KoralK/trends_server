from flask import Flask, request, jsonify
from pytrends.request import TrendReq
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import time
import random

app = Flask(__name__)

# Configure Flask-Caching (Simple in-memory cache)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 3600})  # 1-hour cache

# Configure rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Set up Google Trends API with retries and backoff
pytrends = TrendReq(hl='en-US', tz=360, retries=5, backoff_factor=0.5)

# Set up basic logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    app.logger.info('Home endpoint accessed')
    return "Google Trends API is running"

def fetch_trends_with_backoff(search_query):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            pytrends.build_payload([search_query], cat=0, timeframe='now 7-d', geo='US', gprop='')
            return pytrends.interest_over_time()
        except Exception as e:
            if attempt < max_retries - 1:
                sleep_time = (2 ** attempt) + random.random()
                app.logger.warning(f"Attempt {attempt + 1} failed. Retrying in {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
            else:
                raise e

@cache.cached(timeout=3600, query_string=True)  # Cache for 1 hour
@app.route('/trends', methods=['GET'])
@limiter.limit("5 per minute")  # Add rate limiting
def get_trends():
    search_query = request.args.get('q')

    if not search_query:
        app.logger.error("No search query provided")
        return jsonify({'error': 'Please provide a search query (q)'}), 400

    try:
        app.logger.info(f"Fetching trends data for: {search_query}")
        trends_data = fetch_trends_with_backoff(search_query)

        if trends_data.empty:
            app.logger.warning(f"No data found for query: {search_query}")
            return jsonify({'error': 'No data found for this query'}), 404

        trends_dict = trends_data.reset_index().to_dict(orient='records')
        return jsonify({'search_query': search_query, 'trends': trends_dict})

    except Exception as e:
        app.logger.error(f"Error fetching trends data for '{search_query}': {str(e)}")
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')