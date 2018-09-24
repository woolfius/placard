from flask import Blueprint, jsonify, request
from flask_login import login_required

from _1c_utils import create_obj_1c, create_users_1c
from alchemybase import Person, DepartmentAD, Recommendation, Answer, Question, Priority, Language, \
    MilitaryService, Poll, Department1c
from db import Session
from ldap_utils import candidate_insert, add_new_user_to_AD
from marshmallow_schemas import DepartmentADSchema, PersonSchema, RecommendationSchema, AnswerSchema, \
    PrioritySchema, LanguageSchema, MilitaryServiceSchema, PollSchema, Department1cSchema
from polls_utils import anketa_info, save_anketa_individual
from sql_utils import candidate_to_worker_sql, candidate_update
from ldap_utils import ad


candidate = Blueprint('candidate', __name__)

@candidate.route('/api/get_groups', methods=['GET'])
def grouosad():
    print('start')
    res = ad.search(search_base='CN=Доступ по Wi-Fi,OU=Мои группы,DC=busmarket,DC=ua',
                    search_filter="(objectCategory=group)",
                    attributes=['mail', 'mobile', 'objectSid']
                    )
    if res:
        for entry in ad.response:
            if 'attributes' not in entry:
                continue
            attributes = entry['attributes']
            USER_DN = entry['dn']
            print(USER_DN)
            print(dict(attributes))
    return jsonify('okvbbg')

@candidate.route('/api/candidate/<_id>/<status>', methods=['POST'])
@login_required
def api_catdidate_type_ready(_id, status):
    """
    Зміна типу працівника (активний, відхилений, резерв).
    :param _id: id кандидата
    :param status: ready/reserv/rejected
    """
    session = Session()
    session.query(Person).filter_by(id=_id).update({"type_": status})
    session.commit()
    session.close()
    return 'ok'


@candidate.route('/api/candidate/<status>', methods=['GET'])
@login_required
def api_catdidate_type(status):
    """
    Повертає відсортаваний список по відділам кандидатів.
    :param status: ready/reserv/rejected
    """
    result = {}
    session = Session()
    all_dep = session.query(DepartmentAD).all()
    converter = DepartmentADSchema(many=True)
    list_dep = converter.dump(all_dep).data
    all_dep1c = session.query(Department1c).all()
    converter = Department1cSchema(many=True, only=['id', 'name'])
    list_dep1c = converter.dump(all_dep1c).data

    for arg in list_dep1c:
        dep = {}
        dep.setdefault('id', arg['id'])
        dep.setdefault('department', arg['name'])
        list_dep.append(dep)

    for res in list_dep:
        all_resp = session.query(Person) \
            .filter(Person.type_ == status) \
            .filter(Person.department == res['department']).all()
        converter = PersonSchema(many=True,
                                 only=['name', 'id', 'surname', 'type_', 'fk_poll', 'email', 'mobile_phone', 'skype',
                                       'position'])
        resp = converter.dump(all_resp).data
        if resp:
            candidate = []
            for arg in resp:
                candidate.append(arg)
                candidate_insert(arg)
                result[res['department']] = candidate
    return jsonify(result)

@candidate.route('/api/candidate/info/<_id>', methods=['GET'])
@login_required
def api_catdidate_type_info(_id):
    """
    Повертає загальну інформацію про кандидата.
    :param _id: id кандидата
    """
    session = Session()
    candidate = session.query(Person).filter(Person.id == _id).all()
    converter = PersonSchema(many=True, exclude=['poll'])
    result = converter.dump(candidate).data
    session.close()
    print(result)
    return jsonify(result)


@candidate.route('/api/candidate/towork/<_id>', methods=['POST'])
@login_required
def api_catdidate_ttowork(_id):
    """
    Прийом кандидата на роботу.
    :param _id: ід кандидата
    """
    data = request.json
    print(data)

    # Створення нового користувача в AD
    # sid = add_new_user_to_AD(data)
    # send_info_mail(data)
    sid = 'S-1-5-21-3915682675-1099836910-3992233000-0228'
    # Створення нового користувача в 1С
    # data2 = create_obj_1c(data, sid)
    # res = create_users_1c(data2)
    # Створення нового користувача в MySql
    res = '2554'
    card_number = res
    candidate_to_worker_sql(_id, data, sid, card_number)
    return jsonify(_id)


@candidate.route('/api/candidate/update/<_id>', methods=['POST'])
@login_required
def id_catdidate_update(_id):
    """
    Редагування даних кандидата (зміни відбуваються лише в mysql).
    :param _id: id кандидата
    """
    data = request.json
    candidate_update(data, _id)
    return 'ok'


@candidate.route('/api/<_id>/recomendations', methods=['GET'])
@login_required
def Person_recomendations(_id):
    """
    Повертає записи про те хто може надати рекомендацію по фіз особі за id.
    :param _id: id фіз особи
    Приклад відповіді:
        [
            {
                "name": "Іванов Іван",
                "organization": "Продамо все",
                "phone": "380989005050",
                "position": "начальних відділу торгівлі"
            }
        ]
    """
    session = Session()
    result = session.query(Recommendation).filter(Recommendation.fk_person == _id).all()
    converter = RecommendationSchema(many=True, exclude=['id', 'person'])
    dumps_data = converter.dump(result).data
    return jsonify(dumps_data)


@candidate.route('/anketa/statistics/<int:_id>', methods=['GET'])
@login_required
def anketa_statistic(_id):
    """
    Повертає відповіді анкетування.
    :param _id: ід фіз особи
    """
    session = Session()
    all_records = session.query(Answer).join(Question, Question.id == Answer.fk_question).filter(
        Answer.fk_person == _id).all()
    converter = AnswerSchema(many=True, only=['answer', 'question.question', 'question.id'])
    response = converter.dump(all_records).data
    session.close()
    return jsonify(response)


@candidate.route('/anketa/priority/<int:_id>', methods=['GET'])
@login_required
def anketa_statistic_priority(_id):
    """
    Повертає пріоритети кандидата з анкетування.
    :param _id: ід кандидата
    """
    session = Session()
    all_records = session.query(Priority).filter_by(fk_person=_id).all()
    converter = PrioritySchema(many=True, exclude=['person'])
    response = converter.dump(all_records).data
    session.close()
    return jsonify(response)


@candidate.route('/anketa/language/<int:_id>', methods=['GET'])
@login_required
def anketa_statistic_language(_id):
    """
    Повертає ступінь володіння мовами кандидата з анкетування.
    :param _id: ід кандидата
    """
    session = Session()
    all_records = session.query(Language).filter_by(fk_person=_id).all()
    converter = LanguageSchema(many=True)
    response = converter.dump(all_records).data
    session.close()
    return jsonify(response)


@candidate.route('/anketa/military/<int:_id>', methods=['GET'])
@login_required
def anketa_statistic_militarye(_id):
    """
    Повертає військові зобовязування кандидата з анкетування.
    :param _id: id кандидата
    """
    session = Session()
    all_records = session.query(MilitaryService).filter_by(fk_person=_id).all()
    converter = MilitaryServiceSchema(many=True)
    response = converter.dump(all_records).data
    session.close()
    return jsonify(response)


@candidate.route('/anketa/<_id>', methods=['GET'])
@login_required
def anketa_it(_id):
    """
    Повертає запитання для анкетування.
    :param _id: id анкетування(1/2)
    """
    result = anketa_info(_id)
    return jsonify(result)


@candidate.route('/anketa/save', methods=['GET', 'POST'])
@login_required
def anketa_it_save():
    """
    Збереження результатів проходження анкетування.
    """
    result = request.json

    # _id = result['id']
    _id = save_anketa_individual(result)
    print(_id)
    return jsonify(_id)


@candidate.route('/anketa/list', methods=['GET', 'POST'])
@login_required
def anketa_list():
    """
    Повертає список Анкетувань.
    """
    session = Session()
    records = session.query(Poll).filter_by(status='anketa').all()
    converter = PollSchema(many=True, only=['id', 'name', 'created', 'count_of_complete', 'total_count', 'status',
                                            'description'])
    result = converter.dump(records).data
    return jsonify(result)
