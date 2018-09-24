from itertools import groupby

from flask import Blueprint, jsonify
from flask_login import login_required

from alchemybase import Worker, Person, Position, Department1c, Branch, City
from db import Session
from ldap_utils import candidate_insert
from marshmallow_schemas import WorkerSchema, PersonSchema

person = Blueprint('person', __name__)


@person.route('/users/dep=<string:dep>&status=<string:status>', methods=['GET'])
@login_required
def users_dep(dep, status):
    """
    Фільтр за відділом та статусом фіз особи.
    :param dep:назва відділу
    :param status:active/dismissed/candidate

    """
    result = {}
    session = Session()
    if status == 'active' or status == 'dismissed':
        all_records = session.query(Worker).join(Person, Person.id == Worker.fk_person).join(Position,
                                                                                             Position.id == Worker.fk_position,
                                                                                             isouter=True).join(
            Department1c, Department1c.id == Worker.fk_department, isouter=True) \
            .join(Branch, Branch.id == Worker.fk_branch) \
            .filter(Worker.status == status) \
            .filter(Department1c.name == dep).order_by(Worker.name_ua).all()
        converter = WorkerSchema(many=True,
                                 only=['sid', 'name_ua', 'status', 'skype', 'email','duties',
                                       'ip_phone', 'surname_ua', 'person.mobile_phone', 'person.id',
                                       'person.home_phone', 'position.name', 'department.name'])
        res = converter.dump(all_records).data
    else:
        all_resp = session.query(Person) \
            .filter(Person.type_ == status) \
            .filter(Person.department == dep).order_by(Person.name).all()
        converter = PersonSchema(many=True,
                                 only=['name', 'id', 'surname', 'type_', 'fk_poll', 'email', 'mobile_phone', 'skype',
                                       'position'])
        res = converter.dump(all_resp).data
        for arg in res:
            candidate_insert(arg)
    result[dep] = res
    session.close()
    return jsonify(result)


@person.route('/users/dep=<string:dep>&city=<string:city>&status=<string:status>', methods=['GET'])
@login_required
def users_dep_city(dep, city, status):
    """
    Фільтр за відділом та містом та статусом фіз особи.
    :param dep: відділ
    :param city: місто
    :param status: active/dismisse/candidate
    """
    result = {}
    session = Session()
    if status == 'active' or status == 'dismissed':
        all_records = session.query(Worker).join(Person, Person.id == Worker.fk_person).join(Position,
                                                                                             Position.id == Worker.fk_position,
                                                                                             isouter=True).join(
            Department1c, Department1c.id == Worker.fk_department, isouter=True) \
            .join(Branch, Branch.id == Worker.fk_branch) \
            .join(City, City.id == Branch.fk_city) \
            .filter(Worker.status == status) \
            .filter(City.name == city) \
            .filter(Department1c.name == dep).order_by(Worker.name_ua).all()
        converter = WorkerSchema(many=True,
                                 only=['sid', 'name_ua', 'status', 'skype', 'email','duties',
                                       'ip_phone', 'surname_ua', 'person.mobile_phone', 'person.id',
                                       'person.home_phone', 'position.name', 'department.name'])
        res = converter.dump(all_records).data
    else:
        all_resp = session.query(Person) \
            .filter(Person.type_ == status) \
            .filter(Person.city == city) \
            .filter(Person.department == dep).order_by(Person.name).all()
        converter = PersonSchema(many=True,
                                 only=['name', 'id', 'surname', 'type_', 'fk_poll', 'email', 'mobile_phone', 'skype',
                                       'position'])
        res = converter.dump(all_resp).data
        for arg in res:
            candidate_insert(arg)
    result[dep] = res
    session.close()
    return jsonify(result)


@person.route('/users/city=<string:city>&status=<string:status>', methods=['GET'])
@login_required
def users_city(city, status):
    """
    Фільтр за  містом та статусом фіз особи.
    :param city: місто
    :param status: active/dismisse/candidate
    """
    result = {}
    session = Session()
    if status == 'active' or status == 'dismissed':
        all_records = session.query(Worker).join(Person, Person.id == Worker.fk_person).join(Position,
                                                                                             Position.id == Worker.fk_position,
                                                                                             isouter=True).join(
            Department1c, Department1c.id == Worker.fk_department, isouter=True) \
            .join(Branch, Branch.id == Worker.fk_branch) \
            .join(City, City.id == Branch.fk_city) \
            .filter(Worker.status == status) \
            .filter(City.name == city).order_by(Worker.name_ua) \
            .all()
        converter = WorkerSchema(many=True,
                                 only=['sid', 'name_ua', 'status', 'skype', 'email','duties',
                                       'ip_phone', 'surname_ua', 'person.mobile_phone', 'person.id',
                                       'person.home_phone', 'position.name', 'department.name'])
        res = converter.dump(all_records).data
        users_list_sorted = sorted(res, key=lambda l: l['department']['name'])
        for k, g in groupby(users_list_sorted, lambda l: l['department']['name']):
            department = k
            department_list = list(g)
            result[department] = department_list

    else:
        all_resp = session.query(Person) \
            .filter(Person.type_ == status) \
            .filter(Person.city == city).order_by(Person.name).all()
        converter = PersonSchema(many=True,
                                 only=['name', 'id', 'surname', 'type_', 'fk_poll', 'email', 'mobile_phone', 'skype',
                                       'position', 'department'])
        res = converter.dump(all_resp).data
        for arg in res:
            candidate_insert(arg)
        users_list_sorted = sorted(res, key=lambda l: l['department'])
        for k, g in groupby(users_list_sorted, lambda l: l['department']):
            department = k
            department_list = list(g)
            result[department] = department_list
    session.close()
    return jsonify(result)
