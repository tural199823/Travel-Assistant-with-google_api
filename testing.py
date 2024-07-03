lattitude=53.549438522200916
longtitude=9.985065094736022
from google_api_search import travel_assistant
if __name__ == "__main__":
    travel_assistant(lat=lattitude, lng=longtitude, topics="pizza, restaurants", total_n=15)

