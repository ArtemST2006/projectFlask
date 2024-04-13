import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired



class Place(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'place'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    adress = sqlalchemy.Column(sqlalchemy.String)
    state = sqlalchemy.Column(sqlalchemy.String)
    time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    comments = orm.relationship("Comments", back_populates='place')


class PlaseForm(FlaskForm, SerializerMixin):
    adress = StringField('Адрес', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    submit = SubmitField('Далее')


class PhotoForm(FlaskForm, SerializerMixin):
    photo = FileField("Фото")
    submit = SubmitField('Добавить')