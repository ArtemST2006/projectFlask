from requests import get, post, delete
import pprint

pprint.pprint(get('http://127.0.0.1:8091/api/place/3').json())
pprint.pprint(get('http://127.0.0.1:8091/api/place').json())

