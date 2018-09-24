import json

from flask import Blueprint, jsonify, request
from flask_login import login_required

from _1c_utils import load_users, ChangePerson_1c
from alchemybase import Worker, Person, Position, Department1c, Collision
from app import sync_db
from db import Session
from config import BASE_DN
from ldap_utils import ad, update_user_AD
from marshmallow_schemas import WorkerSchema, Department1cSchema, CollisionSchema
from sql_utils import correction_of_collisions_sql

collision = Blueprint('collision', __name__)


@collision.route('/api/synchronize', methods=['GET', 'POST'])
@login_required
def synchronize():
    """
    Запускає синхронізацію по базах 1с,АД та Mysql.
    """
    sync_db()
    return jsonify('ok')


@collision.route('/api/collisions/user/<sid>', methods=['GET', 'POST'])
@login_required
def collisions_users(sid):
    """
    Отримання даних по невідповідностям працівника за sid-ом з 1с,АД та mysql.
    :param sid: унікальний індифікатор
    """
    session = Session()
    all_records = session.query(Worker).join(Person, Person.id == Worker.fk_person).join(Position,
                                                                                         Position.id == Worker.fk_position,
                                                                                         isouter=True).join(
        Department1c, Department1c.id == Worker.fk_department, isouter=True) \
        .filter(Worker.sid == sid).all()
    converter = WorkerSchema(many=True,
                             only=['sid', 'name_ua', 'name_en', 'surname_en', 'card_number', 'status', 'skype', 'email',
                                   'started_to_work', 'finished_to_work', 'middle_name_ua', 'work_schedule',
                                   'person.passport_id', 'person.date_of_issue', 'person.issued_by',
                                   'ip_phone', 'surname_ua', 'person.mobile_phone', 'person.id', 'person.ipn',
                                   'person.birthday', 'person.home_phone', 'position.name', 'department.name',
                                   'person.place_of_residence', 'person.registration', 'person.marital_status',
                                   'surname_ru', 'name_ru'])
    mysql_ = converter.dump(all_records).data
    user = []
    res = ad.search(search_base='DC=busmarket,DC=ua',
                    search_filter="(&(objectCategory=person)(objectClass=user)(objectSid={sid}))".format(sid=sid),
                    attributes=['mail', 'telephoneNumber', 'sn', 'cn', 'givenName', 'displayName', 'department',
                                'mobile', 'givenName-En', 'givenNameUa', 'cityUa', 'departmentEn',
                                'ipPhone', 'isDeleted', 'userAccountControl', 'l', 'ManagedBy', 'Name', 'CanonicalName',
                                'givenName-En', 'snEn', 'givenNameUa', 'snUa', 'streetAddress',
                                'streetAddressCompany', 'streetAddressCompanyRu', 'co', 'title', 'titleEn', 'titleUa',
                                'departmentEn', 'departmentUa',
                                'company',
                                'companyEn', 'pager', 'st', 'streetAddressCompanyUa', 'streetAddressUa', 'stUa',
                                'postalCode', 'streetAddress', 'street', 'objectSid']
                    )

    if res:
        for entry in ad.response:
            if 'dn' in entry:
                user.append(dict(entry['attributes']))
    print(user)

    result = []
    res = []
    _1c = json.loads(load_users())
    for arg in _1c['data']:
        if arg['SID'] == sid:
            res.append(arg)
    result.append(res)
    result.append(mysql_)
    result.append(user)
    session.close()
    return jsonify(result)


@collision.route('/api/collisions/<sid>', methods=['GET', 'POST'])
@login_required
def correction_of_collisions(sid):
    """
    Метод виправлення невідповідностей між базами 1с, АД та mysql та збереження змін в цих базах.
    :param sid: унікальний індифікатор
    """
    data = request.json
    update_user_AD(data, sid)
    education = []
    family = []
    data2 = {
        "surname": data['snUa'],
        "name": data['givenNameUa'],
        "middlename": data['middlename'],
        "IPN": data['ipn'],
        "SID": sid,
        "address_of_residence": data['registration'],
        "place_of_residence": data['address_residence'],
        "phone": data['mobile'],
        "salary": data['salary'],
        "family": family,
        "education": education,
        "passport": []
    }
    ChangePerson_1c(data2)
    # виправлення колізій в sql
    correction_of_collisions_sql(data)
    return 'ok'


@collision.route('/api/synchronize/get', methods=['GET', 'POST'])
@login_required
def synchronize_get_data():
    """
    Повертає json з працівниками відсортованими по відділах в яких є невідповідності в базах 1с, АД та Mysql.
    Приклад об'єкту що повертаємо

    {
        "eCommerce": [
            {
                "department": "eCommerce",
                "description": "1",
                "fixed": "0",
                "id": 3054,
                "name": "Наталія",
                "position": "Начальник відділу e-commerce",
                "sid": "S-1-5-21-3915682675-1099836910-3992233257-3989",
                "sname": "Сєрякова"
            }
        ]
    }
    """
    result = {}
    session = Session()
    all_records = session.query(Department1c).all()
    converter = Department1cSchema(many=True, only=['name'])
    list_dep = converter.dump(all_records).data
    for res in list_dep:
        all_rcolission = session.query(Collision).filter(Collision.department == res['name']).all()
        converter = CollisionSchema(many=True)
        arg = converter.dump(all_rcolission).data
        result[res['name']] = arg
    session.close()
    return jsonify(result)
