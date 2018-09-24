from flask import Blueprint, jsonify, request

from alchemybase import Experience
from marshmallow_schemas import ExperienceSchema

from db import Session


experience = Blueprint('experience', __name__)


@experience.route('/api/<_id>/experience', methods=['GET'])
def Person_experience(_id):
    """
    Повертає записи з таблиці про досвід роботи для фіз особи. В групу Experience
    :param _id: id фіз особи
    """
    session = Session()
    result = session.query(Experience).filter(Experience.fk_person == _id).all()
    converter = ExperienceSchema(many=True, exclude=['person'])
    dumps_data = converter.dump(result).data
    session.close()
    return jsonify(dumps_data)


@experience.route('/api/<_id>/experience/update', methods=['POST'])
def Person_experience_update(_id):
    """
    Редагує запис в таблиці досвід роботи за id. В групу Experience
    :param _id: id запису в таблиці досвід роботи
    """
    session = Session()
    data = request.json
    session.query(Experience).filter(Experience.id == _id).update(data)
    session.commit()
    session.close()
    return 'ok'


@experience.route('/api/<_id>/experience/add', methods=['POST'])
def Person_experience_add(_id):
    """
    Додає новий запис про досвід роботи фіз особі за id фіз особи. В групу Experience
    :param _id: id фіз особи
    """
    session = Session()
    data = request.json
    data['fk_person'] = _id
    new_experience = Experience(**data)
    session.add(new_experience)
    session.commit()
    session.close()
    return 'ok'


@experience.route('/api/<_id>/experience/delete', methods=['DELETE'])
def Person_experience_delete(_id):
    """
    Видаляє з таблиці запис про досвід роботи за id запису. В групу Experience
    :param _id: id запису в таблиці досвід роботи
    """
    session = Session()
    session.query(Experience).filter(Experience.id == _id).delete()
    session.commit()
    session.close()
    return 'ok'
