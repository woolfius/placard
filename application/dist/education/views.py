from flask import Blueprint, jsonify, request
from flask_login import login_required

from alchemybase import Education, Person, EducationType, EducationInstitution, Specialty
from marshmallow_schemas import EducationSchema, EducationTypeSchema, EducationInstitutionSchema

from db import Session

education = Blueprint('education', __name__)


@education.route('/api/<_id>/education', methods=['GET'])
@login_required
def idOfPerson_education(_id):
    """
    Повертає інформацію про освіту фіз особи. В групу Education
    :param _id: id фізичної особи
    Приклад відповіді json:
    {
        "education": [
            {
                "date_finish": 2009,
                "diplom": ва252145,
                "faculty": "Прикладна математика та інформатика",
                "form_training": "денна",
                "id": 96,
                "main_specialty": "Прикладна математика",
                "main_specialty_year": "2роки",
                "name_institute": "ЛНУ ім.І.Франка",
                "qualification": "спеціаліст",
                "specialty": "прикладна математика та викладач інформатики",
                "type_education": "вища"
            }
        ]
    }
    """
    session = Session()
    result = session.query(Education).join(Person, Person.id == Education.fk_person).filter(Person.id == _id).all()
    converter = EducationSchema(many=True, exclude=['person'])
    dumps_data = converter.dump(result).data
    session.close()
    return jsonify(dumps_data)


@education.route('/api/<_id>/education/update', methods=['POST'])
def Person_education_update(_id):
    """
    Редагування даних в рядку таблиці про освіту за id запису. В групу Education
    :param _id: id запису в таблиці про освіту
    """
    session = Session()
    data = request.json
    session = Session()
    session.query(Education).filter(Education.id == _id).update(data)
    session.commit()
    session.close()
    return 'ok'


@education.route('/api/<_id>/education/add', methods=['POST'])
def Person_education_add(_id):
    """
    Додавання нового запису в таблицю про освіту для фіз особи за id фіз особи. В групу Education
    :param _id: id фіз особи
    """
    session = Session()
    data = request.json
    data['fk_person'] = _id
    new_education = Education(**data)
    session = Session()
    session.add(new_education)
    session.commit()
    session.close()
    return 'ok'


@education.route('/api/<_id>/education/delete', methods=['DELETE'])
def Person_education_delete(_id):
    """
    Видаленні запису про освіту за id цього запису. В групу Education
    :param _id: id запису в таблиці про освіту який потрібно видалити
    """
    session = Session()
    session.query(Education).filter(Education.id == _id).delete()
    session.commit()
    session.close()
    return 'ok'


@education.route('/api/edu/type', methods=['GET'])
@login_required
def api_edu_type():
    """
    Повертає тип освіти. В групу Education
    Приклад відповіді:
    [
        {
            "code": "4        ",
            "id": 5,
            "name": "Аспирантура"
        }
    ]
    """
    session = Session()
    all_records = session.query(EducationType).all()
    converter = EducationTypeSchema(many=True)
    res = converter.dump(all_records).data
    session.close()
    return jsonify(res)


@education.route('/api/edu/institution', methods=['GET'])
@login_required
def api_edu_institute():
    """В групу Education"""
    session = Session()
    all_records = session.query(EducationInstitution).all()
    converter = EducationInstitutionSchema(many=True)
    response = converter.dump(all_records).data
    session.close()
    return jsonify(response)


@education.route('/api/edu/specialty', methods=['GET'])
@login_required
def api_edu_specialty():
    """
    Повертає спеціальність (відноситися до освіти). В групу Education
    Приклад відповіді:
    [
        {
            "code": "000000056",
            "id": 20,
            "name": "автоматизація виробничих процесів та виробництв"
        }
    ]
    """
    session = Session()
    all_records = session.query(Specialty).all()
    converter = Specialty(many=True)
    response = converter.dump(all_records).data
    session.close()
    return jsonify(response)
