import pprint
from io import BytesIO
# Этот класс поможет нам сделать картинку из потока байт

import requests
from PIL import Image


def get_coords_of_name(name):
    try:
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            'geocode': name,
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "format": "json"
        }
        response = requests.get(geocoder_api_server, params=geocoder_params)

        json_response = response.json()

        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        dolg, shir = toponym_coodrinates.split(" ")

        return str(dolg) + ',' + str(shir)
    except Exception:
        return ''


def make_image(adresses):
    lis = []
    for adres in adresses:
        point = get_coords_of_name(adres)
        lis.append(point)

    lis = list(filter(lambda x: x != '', lis))
    points = '~'.join(list(map(lambda x: x + ',pmgnm', lis)))
    print(points)
    map_params = {
        'll': '85.386195,2C57.216735',
        "spn": '50.005,50.005',
        "l": "map",
        'pt': f'{points}'
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"

    response = requests.get(map_api_server, params=map_params)
    print(response)
    Image.open(BytesIO(
        response.content)).show()


make_image(['Рязань Пушкина'])