# Travel Assistant

Travel Assistant is a Python script that helps you find nearby places based on a specified location and search topics. It utilizes the Google Places API to fetch detailed information about places, including reviews, ratings, pricing, and more. The script also summarizes user reviews to provide concise and useful insights.

## Features

- Fetches nearby places based on latitude, longitude, and search topics.
- Extracts and summarizes user reviews for each place.
- Provides detailed information including ratings, price levels, coordinates, and more.
- Generates Google Maps links for easy navigation.
- Saves the data in a JSON file for further analysis.

## Usage

You can use the travel_assistant function to find places and get summarized reviews. Here is a brief overview of how to use the function:

def travel_assistant(lat, lng, topics, api_key):
    """
    Finds nearby places based on provided latitude, longitude, and search topics.

    Parameters:
    lat (float): Latitude of the location.
    lng (float): Longitude of the location.
    topics (str): A string containing relevant search topics, e.g., "restaurant, asian, cheap" or "museum, history, art".
    api_key (str): Your Google Places API key.

    Saves:
    - scraped_data.json: Contains detailed information about the places, including summarized reviews.
    """

## Example
lat = 40.748817
lng = -73.985428
topics = "restaurant, italian, pasta"
api_key = "YOUR_GOOGLE_PLACES_API_KEY"

travel_assistant(lat, lng, topics, api_key)

This will save a file scraped_data.json with the detailed information and summarized reviews of the places.

## Installation

To run this script, you'll need to install the following dependencies:

```bash
pip install requests pandas nltk scikit-learn sumy
python -c "import nltk; nltk.download('stopwords')"
python -c "import nltk; nltk.download('punkt')"


