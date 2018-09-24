from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from alchemybase import Note, Person
from db import Session
from marshmallow_schemas import NoteSchema, PersonSchema

note = Blueprint('note', __name__)


@note.route('/notes', methods=['GET'])
@login_required
def all_notes_Person():
    """
    Повертає всі нотатки. В групу Note
    """
    session = Session()
    all_records = session.query(Note).all()
    converter = NoteSchema(many=True, only=['id', 'name', 'text', 'created', 'type_', 'public', 'id_person',
                                            'fk_author'])
    result = converter.dump(all_records).data
    for arg in result:
        if arg['id_person'] != None:
            records = session.query(Person).filter(Person.id == arg['id_person']).all()
            converter = PersonSchema(many=True, only=['name', 'surname'])
            res = converter.dump(records).data
            arg.setdefault('name_ua', res[0]['name'])
            arg.setdefault('surname', res[0]['surname'])
    session.close()
    return jsonify(result)


@note.route('/api/update/notes', methods=['PUT'])
@login_required
def api_updatenotes():
    """
    Редагування нотатки. В групу Note
    """
    session = Session()
    data = request.json
    session.query(Note).filter_by(id=data['id']).update({"name": data['name'], "text": data['text']})
    session.commit()
    session.close()
    return jsonify('ok')


@note.route('/api/<_id>/notes/add', methods=['POST'])
@login_required
def emailOfPerson_notes_add(_id):
    """
    Додавання нової нотатки на фіз особу. В групу Note
    :param _id: id фіз особи на яку додають нотатку
    """
    session = Session()
    data = request.json
    id_author = session.query(Person.id).filter(Person.email == current_user.get_id()).first()
    data.setdefault('fk_author', id_author[0])
    note = Note(**data)
    session.add(note)
    session.commit()
    session.close()
    return 'ok'


@note.route('/api/notes/delete/<id_>', methods=['DELETE'])
@login_required
def emailOfPerson_notes_delete(id_):
    """
    Видалення нотатки. В групу Note
    :param id_: id нотатки
    """
    session = Session()
    session.query(Note).filter_by(id=id_).delete()
    session.commit()
    session.close()
    return 'ok'


@note.route('/api/notes/<_id>', methods=['GET'])
@login_required
def Person_notes(_id):
    """
    Повертає всі нотатки на фіз особу за її id. В групу Note
    :param _id: id фіз особи
    Приклад відповіді:
    [
        {
            "author_name": "Мар'ян",
            "author_sname": "Реверенда",
            "date": "Sun, 25 Feb 2018 00:00:00 GMT",
            "email": "yevhen.siabrenko@busmarket.ua",
            "id": 1,
            "id_search": 101,
            "name": "Євген",
            "notes.name": "grherne",
            "sname": "Сябренко",
            "text": "текст нотатки",
            "type": null
        }
    ]
    """
    session = Session()
    all_records = session.query(Note).filter(Note.id_person == _id).all()
    converter = NoteSchema(many=True, only=['id', 'name', 'text', 'created', 'type_', 'public', 'id_person',
                                            'fk_author'])
    result = converter.dump(all_records).data
    for arg in result:
        if arg['id_person'] != None:
            records = session.query(Person).filter(Person.id == arg['id_person']).all()
            converter = PersonSchema(many=True, only=['name', 'surname'])
            res = converter.dump(records).data
            arg.setdefault('name_ua', res[0]['name'])
            arg.setdefault('surname', res[0]['surname'])
    session.close()
    return jsonify(result)
