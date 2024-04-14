from flask_restful import reqparse, abort, Api, Resource
from data import  db_session
from data.place import Place
from data.comments import Comments
from data.photo import Photo
from flask import abort, jsonify


def abort_if_Place_not_found(place_id):
    session = db_session.create_session()
    news = session.query(Place).get(place_id)
    if not news:
        abort(404, message=f"Place {place_id} not found")


class NewsResource(Resource):
    def get(self, place_id):
        abort_if_Place_not_found(place_id)
        session = db_session.create_session()
        place = session.query(Place).get(place_id)
        comment = session.query(Comments).filter(Comments.id_place == place_id).all()
        photo = session.query(Photo).filter(Photo.id_place == place_id).first()
        return jsonify({'place': place.to_dict(
            only=('adress', 'state')), 'comment': [comm.to_dict(only=('comm', 'id_user')) for comm in comment]})

    def delete(self, place_id):
        abort_if_Place_not_found(place_id)
        session = db_session.create_session()
        place = session.query(Place).get(place_id)
        comments = session.query(Comments).filter(Comments.id_place == place_id).first()
        photo = session.query(Photo).filter(Photo.id_place == place_id).first()
        session.delete(place)
        try:
            session.delete(comments)
        except:
            pass
        try:
            session.delete(photo)
        except Exception:
            pass

        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('adress', required=True)
parser.add_argument('state', required=True)


class NewsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        place = session.query(Place).all()
        comment = session.query(Comments).filter(Comments.id_place == 3).all()
        return jsonify({'place': [item.to_dict(only=('adress', 'state')) for item in place]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        place = Place(
            adress=args['adress'],
            state=args['state'],
        )
        session.add(place)
        session.commit()
        return jsonify({'id': place.id})