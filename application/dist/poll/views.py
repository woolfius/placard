from flask import Blueprint, request, jsonify
from flask_login import login_required

from alchemybase import Poll, distinct, Statistics, Password
from db import Session
from db_utils import id_generator
from ldap_utils import from_dep
from mail_utils import send_mail, send_sms
from marshmallow_schemas import PollSchema
from polls_utils import poll_save, poll_unpdate, get_poll_statistics, get_poll_statistics_by_dep, \
    get_poll_statistics_by_city, get_poll_statistics_by_dep_city, copy_db

poll = Blueprint('poll', __name__)


@poll.route('/save_poll', methods=['POST', 'GET'])
@login_required
def save_poll():
    """
    Створення та редагування нового опитування. в гуруп Poll
    """
    data = request.json
    _id = poll_save(data)
    return jsonify(_id)


@poll.route('/update_poll/<int:_id>', methods=['GET'])
@login_required
def update_poll(_id):
    """
    Редагування опитування. В групу Poll
    :param id: id опитування
    """
    result = poll_unpdate(_id)
    if result != False:
        return jsonify(result)
    else:
        return 'False'


@poll.route('/poll/<status>', methods=['GET'])
@login_required
def poll_status(status):
    """
    Повертає список опитувань в залежгості до status(в розробці, активні, завершені). в групу Poll
    :param status: status(в розробці, активні, завершені)
    """
    session = Session()
    all_records = session.query(Poll).filter_by(status=status).all()
    converter = PollSchema(many=True, only=['id', 'name', 'created', 'count_of_complete', 'total_count', 'status',
                                            'description'])
    response = converter.dump(all_records).data
    session.close()
    return jsonify(response)


@poll.route('/delete_poll/<_id>', methods=['DELETE'])
@login_required
def delete_poll(_id):
    """
    Видаляє Опитування. в гуруп Poll
    :param _id: id опитування
    """
    session = Session()
    session.query(Poll).filter_by(id=_id).delete()
    session.commit()
    session.close()
    return 'ok'


@poll.route('/statistics/<_id>', methods=['GET'])
@login_required
def statistics(_id):
    """
    Повертає повну статистику по опитуванні. в гуруп Poll
    :param _id: ід опитування
    """
    result = get_poll_statistics(_id)
    if not result:
        return 'False'
    return jsonify(result)


@poll.route('/statistics/dep/<string:dep>/<_id>', methods=['GET'])
@login_required
def statistics_by_dep(dep, _id):
    """
    Повертає статистику опитування по відділу. в гуруп Poll
    :param dep: відділ
    :param _id: ід опитування
    """
    result = get_poll_statistics_by_dep(dep, _id)
    if not result:
        return 'False'
    return jsonify(result)


@poll.route('/statistics/city/<string:city>/<_id>', methods=['GET'])
@login_required
def statistics_by_city(city, _id):
    """
    Повертає статистику опитування по місту. в групу Poll
    :param city:місто
    :param _id:ід опитування
    """
    result = get_poll_statistics_by_city(city, _id)
    if result == False:
        return 'False'
    return jsonify(result)


@poll.route('/statistics/dep/city/<string:dep>/<string:city>/<_id>', methods=['GET'])
@login_required
def statistics_by_dep_city(dep, city, _id):
    """
    Повертає статистику опитування по міста та відділу. в групу Poll
    :param dep: відділ
    :param city: місто
    :param _id: ід опитування
    """
    result = get_poll_statistics_by_dep_city(dep, city, _id)
    if result == False:
        return 'False'
    return jsonify(result)


@poll.route('/statistics/filter/<int:_id>', methods=['GET'])
@login_required
def filter_statistic(_id):
    """
    Повертає в яких відділах та містах було пройдене опитування.
    :param _id: ід опитування
    Приклад відповіді:
    {
        "city": [
            "Луцьк",
            "Львів"
        ],
        "dep": [
            "eCommerce",
            "Інформаційні технології"
        ]
    }
    """
    session = Session()
    response = {}
    dep = []
    city = []
    for arg in session.query(distinct(Statistics.department)).filter_by(fk_poll=_id).all():
        dep.append(arg[0])
    response.setdefault('dep', dep)
    for arg in session.query(distinct(Statistics.city)).filter_by(fk_poll=_id).all():
        city.append(arg[0])
    response.setdefault('city', city)
    session.close()
    return jsonify(response)


@poll.route('/update_status_active/<_id>', methods=['GET', 'POST'])
@login_required
def update_active(_id):
    """
    Публікація опитування, розсилання смс та email з паролями для проходження опитування. В групу Poll
    :param _id: id опитування
    """
    k = 0
    session = Session()
    res = request.json
    all_records = session.query(Poll).filter_by(id=_id).all()
    converter = PollSchema(many=True,
                           only=['id', 'name', 'created', 'count_of_complete', 'total_count', 'status', 'description'])
    result = converter.dump(all_records).data
    for arg in res['email']:
        for step in range(0, arg['copy']):
            k += 1
            password = id_generator()
            dep = from_dep(arg['email'])
            if dep == []:
                data = []
                qw = {}
                qw.setdefault('departmentUa', '')
                qw.setdefault('cityUa', '')
                data.append(qw)
                dep = data
            list_count_poll = session.query(Statistics) \
                .filter(Statistics.department == dep[0]['departmentUa']) \
                .filter(Statistics.city == dep[0]['cityUa']) \
                .filter(Statistics.fk_poll == _id).all()
            if list_count_poll == []:
                statistick = Statistics(total_count=1, fk_poll=_id, department=dep[0]['departmentUa'],
                                        city=dep[0]['cityUa'])
                session.add(statistick)
            else:
                session.query(Statistics) \
                    .filter(Statistics.department == dep[0]['departmentUa']) \
                    .filter(Statistics.city == dep[0]['cityUa']) \
                    .filter_by(fk_poll=_id).update({"total_count": Statistics.total_count + 1})

            passrords = Password(password=password, department=dep[0]['departmentUa'], city=dep[0]['cityUa'],
                                 fk_poll=_id)
            session.add(passrords)
            send_mail(arg['email'], password)
    send_sms(res['mobile'], _id)
    for arg in res['mobile']:
        k += 1
    if int(_id) > 2:
        session.query(Poll).filter_by(id=_id).update({"status": 'active'})
    session.query(Poll).filter_by(id=_id).update({"total_count": k + int(result[0]['total_count'])})
    session.commit()
    session.close()
    return "ok"


@poll.route('/update_status_close/<_id>', methods=['GET'])
@login_required
def update_close(_id):
    """
    Переводить опитування в завершені. в групу Poll
    :param _id: id опитування
    """
    session = Session()
    session.query(Poll).filter_by(id=_id).update({"status": 'close'})
    session.commit()
    session.close()
    return 'ok'


@poll.route('/copy_poll/<int:_id>', methods=['GET'])
@login_required
def copy_poll(_id):
    """
    Копіює опитування. В групу Poll
    :param id: id опитування яке копіюється
    """
    copy_db(_id)
    return 'ok'
