from flask import Blueprint, jsonify, request
from flask_login import login_required

from alchemybase import City, Branch, Department1c, DepartmentAD, Worker, Region, func
from db import Session
from marshmallow_schemas import CitySchema, BranchSchema, Department1cSchema, DepartmentADSchema, \
    RegionSchema

places = Blueprint('places', __name__)


@places.route('/api/city_list', methods=['GET'])
@login_required
def api_city_list():
    """
    Повертає список міст.
    """
    session = Session()
    all_records = session.query(City).all()
    converter = CitySchema(many=True, only=['name'])
    response = converter.dump(all_records).data
    result = []
    for arg in response:
        result.append(arg['name'])
    session.close()
    return jsonify(result)

@places.route('/api/department/<status>', methods=['GET'])
@login_required
def api_department_status(status):
    """
    Повертає список всіх відділів в яких є працівники згідно статусу працівник, звільнений.
    """
    session = Session()
    all_records = session.query(Department1c).join(Worker, Worker.fk_department == Department1c.id)\
        .filter(Worker.status == status).distinct(Department1c.name).order_by(Department1c.name).all()
    converter = Department1cSchema(many=True, only=['name'])
    response = converter.dump(all_records).data
    result = []
    for arg in response:
        result.append(arg['name'])
    return jsonify(result)

@places.route('/api/branch', methods=['GET'])
@login_required
def api_branch_list():
    """
    Повертає список філіалів.
    """
    session = Session()
    all_records = session.query(Branch).all()
    converter = BranchSchema(many=True)
    response = converter.dump(all_records).data
    result = []
    for arg in response:
        result.append(arg['name'])
    session.close()
    return jsonify(result)


@places.route('/api/worker/department', methods=['GET'])
@login_required
def api_worker_dep():
    """
    Повертає повний список всіх відділів.
    """
    session = Session()
    all_records = session.query(Department1c).all()
    converter = Department1cSchema(many=True, only=['name'])
    response = converter.dump(all_records).data
    result = []
    for arg in response:
        result.append(arg['name'])
    session.close()
    return jsonify(result)


@places.route('/api/admin/department', methods=['GET'])
@login_required
def api_admin_department():
    """
    Список відділів в АД.
    """
    session = Session()
    all_dep = session.query(DepartmentAD).all()
    converter = DepartmentADSchema(many=True, only=['department'])
    res = converter.dump(all_dep).data
    result = []
    for arg in res:
        result.append(arg['department'])
    session.close()
    return jsonify(result)

@places.route('/api/admin/deparatment_list', methods=['GET'])
@login_required
def api_department_list():
    """
    Повертає список всіх відділів в яких є працівники.
    """
    session = Session()
    all_records = session.query(Department1c) .distinct(Department1c.name).order_by(Department1c.name).all()
    converter = Department1cSchema(many=True, only=['id','name', 'status'])
    response = converter.dump(all_records).data
    return jsonify(response)

@places.route('/api/admin/deparatment_list/<_id>/<status>', methods=['POST'])
@login_required
def api_department_list_change_status(_id, status):
    """
    Повертає список всіх відділів в яких є працівники.
    """
    session = Session()

    resp = session.query(func.count(Worker.id)).filter(Worker.status == 'active').filter(
        Worker.fk_department == _id).first()
    if resp[0] > 0 and status == 'not active':
        return jsonify('Неможливо деактивувати відділ оскільки в ньому є працівники')
    session.query(Department1c).filter(Department1c.id == _id).update({'status': status})
    session.commit()
    return jsonify('ok')

@places.route('/api/department', methods=['GET'])
@login_required
def api_department():
    """
    Повертає список всіх відділів в яких є працівники.
    """
    session = Session()
    all_records = session.query(Department1c).join(Worker, Worker.fk_department == Department1c.id) \
        .distinct(Department1c.name).all()
    converter = Department1cSchema(many=True, only=['name'])
    response = converter.dump(all_records).data
    result = []
    for arg in response:
        result.append(arg['name'])
    session.close()
    return jsonify(result)


@places.route('/api/admin/branch', methods=['GET'])
@login_required
def api_admin_branch_list():
    """
    Повертає список філіалів.
    """
    session = Session()
    result = session.query(Branch).join(City, City.id == Branch.fk_city).all()
    converter = BranchSchema(many=True,
                             only=['id', 'name', 'name_en', 'zip_code', 'address_ua', 'address_ru', 'address_en',
                                   'fk_city', 'city.name', 'status'])
    dumps_data = converter.dump(result).data
    session.close()
    return jsonify(dumps_data)


@places.route('/api/admin/branch/new', methods=['POST'])
@login_required
def api_admin_branch():
    """
    Створення нового філіалу.
    """
    session = Session()
    data = request.json
    branch_in_db = session.query(Branch).filter(Branch.name == data['name']).first()
    if not branch_in_db:
        data['fk_city'] = session.query(City.id).filter(City.name == data['city']).first()[0]
        del(data['city'])
        new_branch = Branch(**data)
        session.add(new_branch)
        session.commit()
    session.close()
    return 'ok'


@places.route('/api/admin/branch/delete/<_id>', methods=['DELETE'])
@login_required
def api_admin_branch_delete(_id):
    """
    Видалення філіалу.
    :param _id: ід філіалу
    """
    session = Session()
    session.query(Branch).filter_by(id=_id).delete()
    session.commit()
    session.close()
    return 'ok'


@places.route('/api/admin/branch/update/<_id>', methods=['POST'])
@login_required
def api_admin_branch_update(_id):
    """
    Редагування філіалу.
    :param _id: ід філіалу
    """

    session = Session()
    data = request.json
    print(data)
    session.query(Branch).filter(Branch.id == _id).update(data)
    session.commit()
    session.close()
    return 'ok'

@places.route('/api/admin/branch/<_id>/<status>', methods=['POST'])
@login_required
def api_admin_branch_status(_id, status):
    """
    зміна статусу  філіалу
    """
    session = Session()
    resp = session.query(func.count(Worker.id)).filter(Worker.status == 'active').filter(
        Worker.fk_branch == _id).first()
    if resp[0] > 0 and status == 'not active':
        return jsonify('Неможливо деактивувати філіал оскільки в ньому є працівники')
    session.query(Branch).filter(Branch.id == _id).update({'status': status})
    session.commit()
    return jsonify('ok')

@places.route('/api/admin/city/new', methods=['POST'])
@login_required
def api_admin_city():
    """
    Додавання нового міста.
    """
    session = Session()
    data = request.json
    city_in_db = session.query(City).filter(City.name == data['name']).first()
    if not city_in_db:
        new_city = City(**data)
        session.add(new_city)
        session.commit()
    session.close()
    return 'ok'


@places.route('/api/admin/city_list', methods=['GET'])
@login_required
def api_admin_city_list():
    """
    Список міст.
    """
    session = Session()
    result = session.query(City).join(Region, Region.id == City.fk_region).all()
    converter = CitySchema(many=True, only=['name', 'name_en', 'id', 'fk_region', 'region.name', 'region.name_en'])
    dumps_data = converter.dump(result).data
    session.close()
    return jsonify(dumps_data)


@places.route('/api/admin/region_list', methods=['GET'])
@login_required
def api_admin_region_list():
    """
    Повертає список областей.
    """
    session = Session()
    result = session.query(Region).all()
    converter = RegionSchema(many=True, only=['id', 'name'])
    dumps_data = converter.dump(result).data
    session.close()
    return jsonify(dumps_data)


@places.route('/api/admin/city/delete/<_id>', methods=['DELETE'])
@login_required
def api_admin_city_delete(_id):
    """
    Видалення міста.
    :param _id: ід міста
    """
    session = Session()
    session.query(City).filter_by(id=_id).delete()
    session.commit()
    session.close()
    return 'ok'


@places.route('/api/admin/city/update/<_id>', methods=['POST'])
@login_required
def api_admin_city_update(_id):
    """
    Редагування міста.
    :param _id: id міста
    """
    session = Session()
    data = request.json
    session.query(City).filter(City.id == _id).update(data)
    session.commit()
    session.close()
    return 'ok'
