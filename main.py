# noinspection PyUnresolvedReferences
import pprint
import wikipedia
from os import abort
from flask import Flask, render_template, redirect, request, make_response, jsonify
from flask_restful import abort, Api

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms.user import LoginForm, RegisterForm, CommentsForm
from data import db_session
from data.users import User
from data.place import Place, PlaseForm, PhotoForm
from data.photo import Photo
from data.comments import Comments
from data import news_resources

from io import BytesIO

import requests
from PIL import Image

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
CURRENT_ADDRESS_FOR_WIKI = ''


def save_picture_post(filename):
    return filename.read()


def map_my_chose(file_name, number):
    Image.open(BytesIO(
        file_name.read())).convert('RGB').save(f'static/light_photo/photo{number}.jpg')


def get_coords_of_name(name):  # координаты по названию
    global CURRENT_ADDRESS_FOR_WIKI
    try:
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            'geocode': name,
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "format": "json"
        }
        response = requests.get(geocoder_api_server, params=geocoder_params)

        json_response = response.json()
        CURRENT_ADDRESS_FOR_WIKI = json_response["response"]['GeoObjectCollection']['featureMember'][0]['GeoObject'][
            'metaDataProperty']['GeocoderMetaData']['Address']['Components'][-1]['name']

        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        dolg, shir = toponym_coodrinates.split(" ")

        return str(dolg) + ',' + str(shir)
    except Exception:
        CURRENT_ADDRESS_FOR_WIKI = ''
        return ''


def make_image(adresses):  # одна большая карта
    lis = []
    for adres in adresses:
        try:
            point = get_coords_of_name('+'.join(adres.adress.split()))
            lis.append(point)
        except Exception:
            pass

    points = '~'.join(list(map(lambda x: x + ',pmgnm', lis)))

    map_params = {
        'll': '79.519631,59.696317',
        "spn": '20.005,20.005',
        "l": "map",
        'pt': f'{points}'
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)

    try:
        Image.open(BytesIO(
            response.content)).convert('RGB').save('static/maper.jpg')
    except Exception:
        pass


def give_indexs(count, text):
    try:
        ch = len(text) // count
        if text.count('.') == 0:
            raise Exception
        text += '   .'
        lis = []
        CONSTS = '.?!)]}"'
        for i in range(count):
            lis.append(text[:ch])
            text = text[ch + 1:]

        for i in range(count - 1):
            a = lis[i]
            b = lis[i + 1]
            if a[-1] not in CONSTS:
                ind = min([b.index('.') if '.' in b else len(b), b.index('?') if '?' in b else 10 ** 20,
                           b.index('!') if '?' in b else 10 ** 20])
                lis[i] = a + b[:ind + 1]
                lis[i + 1] = b[ind + 1:]
        return lis
    except Exception:
        return [text, False, False, False]


def make_state(adress):  # википедия
    try:
        wikipedia.set_lang('ru')
        s = wikipedia.summary(CURRENT_ADDRESS_FOR_WIKI, sentences=5)
        silka = wikipedia.page(adress).url

        return s, silka
    except Exception:
        return None, None


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def index():  # главная страница
    db_sess = db_session.create_session()
    place_adress = db_sess.query(Place)
    make_image(place_adress)
    return render_template("index.html", title='test')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():  # лоогин
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():  # регистрация
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def make_one_map(adress):  # делаем карту одного места
    point = get_coords_of_name('+'.join(adress.split()))

    map_params = {
        'll': f'{point}',
        "spn": '7.005,7.005',
        "l": "map",
        'pt': f'{point},pmgnm'
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)

    try:
        Image.open(BytesIO(
            response.content)).convert('RGB').save('static/light_photo/limaps.jpg')
        return True
    except Exception:
        return False


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route('/list_place')
def list_place():  # все места
    db_sess = db_session.create_session()
    place = db_sess.query(Place)
    return render_template('many_place.html', place=place)


@app.route('/add_place/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):  # изменение
    form = PlaseForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        place = db_sess.query(Place).filter(Place.id == id,
                                            ).first()
        if place:
            form.adress.data = place.adress
            form.content.data = place.state
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        place = db_sess.query(Place).filter(Place.id == id).first()
        if place:
            place.adress = form.adress.data
            place.state = form.content.data
            db_sess.commit()
            return redirect(f'/add_photos/{id}')
        else:
            abort(404)
    return render_template('add_place.html',
                           title='Редактирование',
                           form=form, messenge=False
                           )


@app.route('/add_place', methods=['GET', 'POST'])
@login_required
def add_place():  # добавить место
    form = PlaseForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        place = Place()

        current_ad = db_sess.query(Place).filter(Place.adress == form.adress.data).first()
        if current_ad:
            return render_template('add_place.html', messenge='Уже есть такое место', title='Добавление места',
                                   form=form)

        place.adress = form.adress.data
        place.state = form.content.data
        k = make_one_map(place.adress)
        place.current_name = CURRENT_ADDRESS_FOR_WIKI
        st, sl = make_state(place.current_name)

        place.wiki = st
        place.ssilka = sl

        if k:
            place.map_photo = open('static/light_photo/limaps.jpg', 'rb').read()

        text = request.files['filetxt']
        if text:
            srtka = text.read().decode('utf-8')
            place.state = srtka

        db_sess.add(place)

        id_last_place = db_sess.query(Place).filter(Place.adress == form.adress.data).first().id
        db_sess.commit()

        return redirect(f'/add_photos/{id_last_place}')
    return render_template('add_place.html', title='Добавление места',
                           form=form, messenge=False)


@app.route('/add_photos/<int:id>', methods=['GET', 'POST'])
@login_required
def add_photos(id):  # фото
    form = PhotoForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        photo = Photo()

        f1 = request.files['file1']
        f2 = request.files['file2']
        f3 = request.files['file3']
        f4 = request.files['file4']

        photo.photo1 = save_picture_post(f1)
        photo.photo2 = save_picture_post(f2)
        photo.photo3 = save_picture_post(f3)
        photo.photo4 = save_picture_post(f4)

        if not photo.photo3:
            photo.photo3 = photo.photo4
            photo.photo4 = None

        if not photo.photo2:
            photo.photo2 = photo.photo3
            photo.photo3 = photo.photo4
            photo.photo4 = None

        if not photo.photo1:
            photo.photo1 = photo.photo2
            photo.photo2 = photo.photo3
            photo.photo3 = photo.photo4
            photo.photo4 = None

        photo.id_place = id
        db_sess.add(photo)
        db_sess.commit()
        return redirect('/list_place')
    return render_template('add_photos.html', title='Фотографии', form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def place_delete(id):  # удалить место
    db_sess = db_session.create_session()
    place = db_sess.query(Place).filter(Place.id == id,
                                        ).first()
    photo = db_sess.query(Photo).filter(Photo.id_place == id).first()
    coment = db_sess.query(Comments).filter(Comments.id_place == id)
    for el in coment:
        db_sess.delete(el)

    if place:
        db_sess.delete(place)
        try:
            db_sess.delete(photo)
        except Exception:
            pass
        db_sess.commit()
    else:
        abort(404)
    return redirect('/list_place')


@app.route('/zaaupa/<int:id>', methods=['GET', 'POST'])
@login_required
def infopov(id):  # подробнее о месте
    db_sess = db_session.create_session()
    one_placer = db_sess.query(Place).filter(Place.id == id).first()
    comments = db_sess.query(Comments).filter(Comments.id_place == id)
    map_photo = one_placer.map_photo
    if map_photo:
        Image.open(BytesIO(
            map_photo)).convert('RGB').save('static/light_photo/limaps.jpg')

    count = 0

    photos = db_sess.query(Photo).filter(Photo.id_place == id).first()
    if photos.photo1:
        count += 1
        Image.open(BytesIO(
            photos.photo1)).convert('RGB').save('static/run_photo/photo1.jpg')

    if photos.photo4:
        count += 1
        Image.open(BytesIO(
            photos.photo4)).convert('RGB').save('static/run_photo/photo4.jpg')

    if photos.photo2:
        count += 1
        Image.open(BytesIO(
            photos.photo2)).convert('RGB').save('static/run_photo/photo2.jpg')

    if photos.photo3:
        count += 1
        Image.open(BytesIO(
            photos.photo3)).convert('RGB').save('static/run_photo/photo3.jpg')

    texsts = give_indexs(count, one_placer.state)
    n = 4 - len(texsts)
    texsts.extend([False] * n)

    form = CommentsForm()
    if form.validate_on_submit():
        coment = Comments(
            comm=form.comment.data,
            id_user=current_user.id,
            id_place=id
        )
        db_sess.add(coment)
        db_sess.commit()
    return render_template('info_lupa.html', title='Подробнее', form=form, oneplace=one_placer,
                           photos=photos, comments=comments, text1=texsts[0], text2=texsts[1],
                           text3=texsts[2], text4=texsts[3], map_photo=map_photo)


def main():
    db_session.global_init("db/travel.db")
    api.add_resource(news_resources.NewsListResource, '/api/place')
    api.add_resource(news_resources.NewsResource, '/api/place/<int:place_id>')

    app.run(port=8092, host='127.0.0.1')


if __name__ == '__main__':
    main()
