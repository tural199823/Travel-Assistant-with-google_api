from google_api_search import travel_assistant

lattitude=54.32200545150133
longtitude=10.14140860344599
#
if __name__ == "__main__":
    travel_assistant(lat=lattitude, lng=longtitude, topics="restaurants", api_key="your_api_key")

