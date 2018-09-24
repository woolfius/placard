from flask import Blueprint, jsonify, request
from flask_login import login_required
from db import Session
from alchemybase import Family, Worker,Person, or_, and_, extract, func, Department1c, Branch, City
from marshmallow_schemas import FamilySchema,WorkerSchema
from datetime import datetime

family = Blueprint('family', __name__)


@family.route('/api/<_id>/family', methods=['GET'])
@login_required
def idOfPerson_family(_id):
    """
    Повертає дані про сімю фізичної особи за id фізичної особи. В групу Family
    :param _id: id фізичної особи
    Приклад відповіді:
    [
        {
            "date": "Sat, 01 Jan 2000 00:00:00 GMT",
            "id": 11,
            "name": "Іван",
            "position": "дизайнер",
            "sname": "Іванов",
            "type": "чоловік",
            "work_place": "Google"
        }
    ]
    """

    session = Session()
    result = session.query(Family).filter(Family.fk_person == _id).all()
    converter = FamilySchema(many=True, only=['id', 'name', 'surname', 'birthday', 'type_', 'workplace', 'position'])
    dumps_data = converter.dump(result).data
    session.close()
    return jsonify(dumps_data)


@family.route('/api/<_id>/family/update', methods=['POST'])
def Person_family_update(_id):
    """
    Редагування даних по таблиці сім'ї за її іd. В групу Family
    :param _id: id рядка таблиці для якої здійснюємо зміни
    """
    session = Session()
    data = request.json
    if data['birthday']:
        data['birthday'] = data['birthday'][0:10]
    else:
        data.pop('birthday')
    session = Session()
    session.query(Family).filter(Family.id == _id).update(data)
    session.commit()
    session.close()
    return 'ok'


@family.route('/api/<_id>/family/add', methods=['POST'])
def Person_family_add(_id):
    """
    Додавання даних про нового члена сім"ї в таблицю family.  В групу Family
    :param _id: id фізичної особи
    """
    session = Session()
    data = request.json
    if data['birthday']:
        data['birthday'] = data['birthday'][0:10]
    data['fk_person'] = _id
    new_family_member = Family(**data)
    session.add(new_family_member)
    session.commit()
    session.close()
    return 'ok'


@family.route('/api/<_id>/family/delete', methods=['DELETE'])
def Person_family_delete(_id):
    """
    Видаляє запис з таблиці family за id запису.  В групу Family
    :param _id: id запису в таблиці
    """
    session = Session()
    session.query(Family).filter(Family.id == _id).delete()
    session.commit()
    session.close()
    return 'ok'

@family.route('/api/children', methods=['GET', 'POST'])
@login_required
def api_admin_worker_active():
    """
    Повертає статистику по кількості по кількості дітей до 14 років
    """
    session = Session()
    data = request.json
    current_date = datetime.strptime(str(data['date'][0:10]), "%Y-%m-%d").date()
    result = {}
    children = session.query(Worker) \
        .join(Person, Worker.fk_person == Person.id) \
        .join(Family, Person.id == Family.fk_person) \
        .join(Department1c, Department1c.id == Worker.fk_department) \
        .join(Branch, Branch.id == Worker.fk_branch).join(City, City.id == Branch.fk_city) \
        .filter(Department1c.name.like(data['dep'])) \
        .filter(City.name.like(data['city'])) \
        .filter(Worker.status == 'active') \
        .filter(Family.type_ == 'Дитина') \
        .filter(or_(and_(current_date.year - extract('year', Family.birthday) < 14),
                    and_(current_date.year - extract('year', Family.birthday) == 14,
                         current_date.month <= extract('month', Family.birthday),
                         current_date.day < extract('day', Family.birthday)))).all()
    converter = WorkerSchema(many=True, only=['name_ua', 'surname_ua', 'fk_person', 'position.name',
                                              'department.name'])
    resp = converter.dump(children).data
    department = []
    k = 0
    for arg in resp:
        k += 1
        if not arg['department']['name'] in department:
            department.append(arg['department']['name'])
            worker = []
            for res in resp:
                if arg['department']['name'] == res['department']['name']:
                    count = session.query(func.count(Family.id)).join(Person, Person.id == Family.fk_person).filter(
                        Family.fk_person == res['fk_person']).filter(Family.type_ == 'Дитина').filter(
                        or_(and_(current_date.year - extract('year', Family.birthday) < 14),
                            and_(current_date.year - extract('year', Family.birthday) == 14,
                                 current_date.month <= extract('month', Family.birthday),
                                 current_date.day < extract('day', Family.birthday)))).first()
                    res.setdefault('count', count[0])
                    records = session.query(Family).join(Person, Person.id == Family.fk_person).filter(
                        Family.fk_person == res['fk_person']).filter(Family.type_ == 'Дитина').filter(
                        or_(and_(current_date.year - extract('year', Family.birthday) < 14),
                            and_(current_date.year - extract('year', Family.birthday) == 14,
                                 current_date.month <= extract('month', Family.birthday),
                                 current_date.day < extract('day', Family.birthday)))).all()
                    converter = WorkerSchema(many=True, only=['name', 'birthday'])
                    child = converter.dump(records).data
                    res.setdefault('children', child)
                    worker.append(res)

            result.setdefault(arg['department']['name'], worker)
    return jsonify(result)
