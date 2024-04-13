import pprint
from io import BytesIO
# Этот класс поможет нам сделать картинку из потока байт

import requests
from PIL import Image


def get_coords_of_name(name):
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




def make_image(adresses):
    lis = []
    for adres in adresses:
        try:
            point = get_coords_of_name('+'.join(adres.split()))
            lis.append(point)
        except Exception:
            pass

    points = '~'.join(list(map(lambda x: x + ',pmgnm', lis)))
    print(points)


    map_params = {
        'll': '79.519631,59.696317',
        "spn": '20.005,20.005',
        "l": "map",
        'pt': f'{points}'
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)

    Image.open(BytesIO(
        response.content)).show()


make_image(['Рязань Пушкина 18 к2', 'Улан-Удэ', 'ывдоар'])