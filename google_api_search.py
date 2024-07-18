import requests
import pandas as pd
import json
from json import loads
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# pip install nltk
# pip install scikit-learn
# pip install sumy
# python -c "import nltk; nltk.download('stopwords')"
# python -c "import nltk; nltk.download('punkt')"


def travel_assistant(lat, lng, topics, api_key):
    """
    Finds nearby places based on provided latitude, longitude, and search topics.

    Parameters:
    lat (float): Latitude of the location.
    lng (float): Longitude of the location.
    topics (str): A string containing relevant search topics, e.g., "restaurant, asian, cheap" or "museum, history, art".

    The summarize_reviews function also includes a summarizer for the reviews of each place.
    The summarizer helps to condense multiple reviews into a few sentences, making it easier
    to understand and utilize the key points from user reviews.

    Saves:
    - scraped_data.json: Contains detailed information about the places, including summarized reviews
    """

    try:
        # Scrape the nearby places
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "keyword": topics,
            "location": f"{lat}, {lng}",
            "radius": 2000,
            "key": api_key,
            "opennow": True
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
        else:
            raise Exception(f"Travel Assistant Error: Error fetching nearby places: {response.status_code}")

        data = data['results']

        # Extract relevant information from data
        rating = []
        pricing = []
        place_ids = []
        names = []
        urls = []
        for i in range(len(data)):
            names.append(data[i]['name'])
            rating.append(data[i]['rating'])
            pricing.append(data[i].get('price_level', None))
            place_ids.append(data[i].get('place_id', None))
            urls.append(
                f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_ids[i]}&key={api_key}&language=de")

        # Check for duplicate names
        counts = {}
        unique_store_names = []
        for name in names:
            if name not in counts:
                counts[name] = 1
                unique_store_names.append(name)
            else:
                counts[name] += 1
                new_name = f"{name} {counts[name]}"
                unique_store_names.append(new_name)

        names = unique_store_names
        data_dict = {'Name': names, 'Rating': rating, 'Price Score': pricing, 'Place_ids': place_ids, 'Place urls': urls}
        df = pd.DataFrame.from_dict(data_dict)

        reviews_by_place = {}
        description_by_place = {}
        coordinates_by_place = {}
        distance_by_place = {}
        map_links_by_place = {}
        indoor_by_place = {}

        for i in range(len(urls)):
            review_responses = requests.get(urls[i])
            if review_responses.status_code == 200:
                review_data = review_responses.json()
                place_name = names[i]

                # REVIEWS OF A PLACE
                reviews = []
                for review in review_data['result'].get('reviews', []):
                    reviews.append(review['text'])
                reviews_by_place[place_name] = reviews

                # DESCRIPTION OF A PLACE
                if 'editorial_summary' in review_data['result']:
                    description = review_data['result']['editorial_summary']['overview']
                    description_by_place[place_name] = description

                # COORDINATES OF A PLACE
                coordinate = review_data['result']['geometry']['location']
                coordinates_by_place[place_name] = coordinate

                # INDOOR EATING OF A PLACE
                indoor_eating = review_data['result']['dine_in']
                indoor_by_place[place_name] = indoor_eating
            else:
                raise Exception(f"Travel Assistant Error: Error fetching place details: {review_responses.status_code}")

        # Create a dictionary of addresses from lat and lng coordinates
        for i in range(len(names)):
            map_links = []
            place_name = names[i]
            id_data = place_ids[i]
            map_links.append(f"https://www.google.com/maps?q=place_id:{id_data}")
            map_links_by_place[place_name] = map_links

        # Create a list of distances from the origin to nearby places
        destination_coords = "|".join([f"{v['lat']},{v['lng']}" for v in coordinates_by_place.values()])
        url_distance = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params_distance = {
            "destinations": destination_coords,
            "origins": f"{lat}, {lng}",
            "mode": "walking",
            "key": api_key,
        }

        response_distance = requests.get(url_distance, params=params_distance)
        if response_distance.status_code == 200:
            distance_data = response_distance.json()
        else:
            raise Exception(f"Travel Assistant Error: Error fetching distance data: {response_distance.status_code}")

        for i in range(len(coordinates_by_place)):
            place_name = names[i]
            distance = distance_data['rows'][0]['elements'][i]['distance']['text']
            distance_by_place[place_name] = distance

        pd.options.display.max_colwidth = 90

        # Construct review dataframe
        review_df = pd.DataFrame.from_dict(reviews_by_place, orient='index').reset_index()
        review_df.columns = ['Name', 'Review_1', 'Review_2', 'Review_3', 'Review_4', 'Review_5']

        final_reviews = review_df.to_json(orient="records")

        parsed_1 = loads(final_reviews)

        '''BELOW CODE SUMMARIZES ALL THE REVIEWS'''
        def concatenate_reviews(data):
            concatenated_reviews = {}
            for restaurant in data:
                index = restaurant.get('Name')
                all_reviews = ""
                for key in restaurant:
                    if key.startswith('Review'):
                        all_reviews += restaurant[key] + " "
                concatenated_reviews[index] = all_reviews.strip()

            return concatenated_reviews

        concatenated_reviews = concatenate_reviews(parsed_1)

        german_stop_words = stopwords.words('german')
        words_to_keep = {'nicht', 'nein', 'kein'}

        custom_stop_words = [word for word in german_stop_words if word not in words_to_keep]

        vect = CountVectorizer(stop_words=custom_stop_words)

        def stop_word_removal(x):
            token = x.split()
            return ' '.join([w for w in token if not w in custom_stop_words])

        processed_reviews = {restaurant: stop_word_removal(review) for restaurant, review in
                             concatenated_reviews.items()}

        def summarize_reviews(reviews, num_sentences=3):
            summaries = {}

            for restaurant, review in reviews.items():
                parser = PlaintextParser.from_string(review, Tokenizer("english"))
                summarizer = LsaSummarizer()
                summary = summarizer(parser.document, sentences_count=num_sentences)

                summary_sentences = [str(sentence) for sentence in summary]

                summaries[restaurant] = "\n".join(summary_sentences)

            return summaries

        summary_reviews = summarize_reviews(concatenated_reviews)
        # Add new columns to the DataFrame
        df = df.assign(
            **{
                'Google map link': list(map_links_by_place.values()),
                'Distance to a place': list(distance_by_place.values()),
                'Indoor eating place': list(indoor_by_place.values()),
                'Summary of reviews': list(summary_reviews.values())
            }
        )
        scraped_data = df.to_dict(orient='records')
        with open("scraped_data.json", "w") as save_file:
            json.dump(scraped_data, save_file, indent=4)
        # return scraped_data

    except Exception as e:
        raise Exception(f"Travel Assistant Error: {str(e)}")