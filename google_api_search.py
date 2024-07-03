import requests
import pandas as pd
from json import loads, dumps
import json
from deep_translator import GoogleTranslator

def travel_assistant(lat, lng, topics, total_n):
    ''

    '''Topics should be a string, containing all the relevant information about what exactly are we searching,
    The examples are: topics = "restaurant, asian, cheap", or "museum, history, art" etc.'''

    '''Lat and lng should be given as number inputs, which is taken from a geolocation of a person'''

    '''Total_n accounts for a number of places we want to return. By default, google places api returns 20
    If we want to restrain it to, say 5, we can add that parameter and take first 5 places returned and use only them.
    This code returns places based on their importance and relevance. If you want to return places based on their distance,
    you can set rankby to distance in the params section.'''

    # Scrape the nearby places
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "keyword": topics,
        "location": f"{lat}, {lng}",
        "radius": 2000,
        "key": "AIzaSyBYtq7koQNE1I66iDEPbUtGvFWAif6ZJr0",
        "opennow": True
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Error: {response.status_code}")

    data = data['results'][:total_n]

    # Take the relevant information from data.json and pass them to a dataframe
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
            f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_ids[i]}&key=AIzaSyBYtq7koQNE1I66iDEPbUtGvFWAif6ZJr0&language=de")

    # To check for duplicate names
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
    dict = {'Name': names, 'Rating': rating, 'Price Score': pricing, 'Place_ids': place_ids, 'Place urls': urls}
    df = pd.DataFrame.from_dict(dict)

    reviews_by_place = {}
    description_by_place = {}
    coordinates_by_place = {}
    opening_hours_by_place = {}
    distance_by_place = {}
    map_links_by_place = {}

    for i in range(len(urls)):
        review_responses = requests.get(urls[i])

        if review_responses.status_code == 200:
            review_data = review_responses.json()
            place_name = names[i]

            # REVIEWS OF A PLACE
            reviews = []

            for review in review_data['result'].get('reviews', []):
                reviews.append(GoogleTranslator(source='auto', target='en').translate(review['text']))

            reviews_by_place[place_name] = reviews

            # DESCRIPTION OF A PLACE

            if 'editorial_summary' in review_data['result']:
                description = review_data['result']['editorial_summary']['overview']
                description_by_place[place_name] = description

            # COORDINATES OF A PLACE

            coordinate = review_data['result']['geometry']['location']
            coordinates_by_place[place_name] = coordinate

            # OPENING HOURS OF A PLACE
            opening_hours = review_data['result']['opening_hours']['weekday_text']
            opening_hours_by_place[place_name] = opening_hours

        else:
            print(f"Error: {review_responses.status_code}")

    # Create a dictionary of adresses from lat and lng coordinates

    for i in range(len(coordinates_by_place)):
        place_name = names[i]
        map_link = f"https://www.google.com/maps?q={coordinates_by_place[place_name]['lat']},{coordinates_by_place[place_name]['lng']}"
        map_links_by_place[place_name] = map_link

    # Create a list of distance from an origin to nearby places
    destination_coords = "|".join([f"{v['lat']},{v['lng']}" for v in coordinates_by_place.values()])

    url_distance = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params_distance = {
        "destinations": destination_coords,
        "origins": f"{lat}, {lng}",
        "mode": "walking",
        "key": "AIzaSyBYtq7koQNE1I66iDEPbUtGvFWAif6ZJr0",
    }

    response_distance = requests.get(url_distance, params=params_distance)

    if response_distance.status_code == 200:
        distance_data = response_distance.json()
    else:
        print(f"Error: {response_distance.status_code}")

    for i in range(len(coordinates_by_place)):
        place_name = names[i]
        distance = distance_data['rows'][0]['elements'][i]['distance']['text']
        distance_by_place[place_name] = distance

    # Construct review dataframe
    pd.options.display.max_colwidth = 60
    review_df = pd.DataFrame.from_dict(reviews_by_place, orient='index')
    review_df.reset_index(inplace=True)
    review_df.rename(columns={0: "Review_1", 1: "Review_2", 2: "Review_3", 3: "Review_4", 4: "Review_5"}, inplace=True)

    # Concatenate final dataframe
    final_data = pd.concat([df, review_df[["Review_1", "Review_2", "Review_3", "Review_4", "Review_5"]]], axis=1)
    final_data['Google map link'] = map_links_by_place.values()
    final_data['Distance to a place'] = distance_by_place.values()
    final_data['Opening hours'] = opening_hours_by_place.values()

    # Save the dataframe to a json file
    result = final_data.to_json(orient="records")
    parsed = loads(result)
    save_file = open("scraped_data.json", "w")
    json.dump(parsed, save_file, indent=6)
    save_file.close()

    return final_data
