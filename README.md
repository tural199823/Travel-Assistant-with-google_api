# Travel Assistant

Travel Assistant is a Python script that helps you find nearby places based on a specified location and search topics. It utilizes the Google Places API to fetch detailed information about places, including reviews, ratings, pricing, and more. The script also summarizes user reviews to provide concise and useful insights.

## Features

- Fetches nearby places based on latitude, longitude, and search topics.
- Extracts and summarizes user reviews for each place.
- Provides detailed information including ratings, price levels, coordinates, and more.
- Generates Google Maps links for easy navigation.
- Saves the data in a JSON file for further analysis.

## Installation

To run this script, you'll need to install the following dependencies:

```bash
pip install requests pandas nltk scikit-learn sumy
python -c "import nltk; nltk.download('stopwords')"
python -c "import nltk; nltk.download('punkt')"
