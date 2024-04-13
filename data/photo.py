import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired



class Photo(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'photo'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    id_place = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("place.id"))
    photo1 = sqlalchemy.Column(sqlalchemy.BLOB)
    photo2 = sqlalchemy.Column(sqlalchemy.BLOB)
    photo3 = sqlalchemy.Column(sqlalchemy.BLOB)
    photo4 = sqlalchemy.Column(sqlalchemy.BLOB)

    place = orm.relationship('Place')
