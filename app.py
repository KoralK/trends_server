from flask import Flask, request, jsonify
from pytrends.request import TrendReq

app = Flask(__name__)

# Initialize Google Trends API
pytrends = TrendReq(hl='en-US', tz=360)

@app.route('/')
def home():
    return "Google Trends API is running"

@app.route('/trends', methods=['GET'])
def get_trends():
    # Get search query from the request
    search_query = request.args.get('q')

    if not search_query:
        return jsonify({'error': 'Please provide a search query (q)'}), 400

    try:
        # Build the payload for the search query
        pytrends.build_payload([search_query], cat=0, timeframe='now 7-d', geo='US', gprop='')

        # Get interest over time for the search query
        trends_data = pytrends.interest_over_time()

        # Convert the trends data to a dictionary and send as JSON response
        if not trends_data.empty:
            trends_dict = trends_data.reset_index().to_dict(orient='records')
            return jsonify({'search_query': search_query, 'trends': trends_dict})
        else:
            return jsonify({'error': 'No data found for this query'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
