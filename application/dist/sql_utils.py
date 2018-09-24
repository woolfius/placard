from db_utils import vacation_user

from alchemybase import Person, Document, Worker, Salary, Vacation, Education, MilitaryService, Experience, Family, \
    Department1c, Position, Branch, Collision
from db import Session


def create_new_worker_sql(data, sid, card_number):
    """
    Створення нового користувача в sql
    :param data: обєкт з анкети
    :param sid: sid з АД
    :param card_number: з 1с
    """
    session = Session()
    mail = data['AD']['givenName-En'] + '.' + data['AD']['snEn'] + '@busmarket.ua'
    id_dep = session.query(Department1c.id).filter(Department1c.name == data['department']).first()
    id_position = session.query(Position.id).filter(Position.name == data['position']).first()
    id_branch = session.query(Branch.id).filter(Branch.name == data['branch']).first()
    data['person']['birthday'] = data['person']['birthday'][0:10]
    data['person']['date_of_issue'] = data['person']['date_of_issue'][0:10]
    data['worker']['started_to_work'] = data['worker']['started_to_work'][0:10]
    if data['permissions']['email'] == '1':
        data['person']['email'] = mail.lower()
        data['worker']['email'] = mail.lower()
    data['worker']['card_number'] = card_number
    # photo = data['photo']
    person = Person(**data['person'])
    session.add(person)
    session.flush()
    # if photo != '':
    #     document = Document(name='фотографія', file_type='', file=photo.encode('utf-8'), type_='', fk_person=person.id)
    #     db.session.add(document)
    data['worker']['sid'] = sid
    data['worker']['fk_person'] = person.id
    data['worker']['fk_position'] = id_position[0]
    data['worker']['fk_branch'] = id_branch[0]
    data['worker']['fk_department'] = id_dep[0]
    worker = Worker(**data['worker'])
    session.add(worker)
    session.flush()
    id_worker = worker.id
    salary = Salary(salary=data['salary'], fk_position=id_position[0], fk_worker=id_worker)
    session.add(salary)
    # Додавання освіти
    for arg in data['education']:
        arg['fk_person'] = person.id
        education = Education(**arg)
        session.add(education)
    # Додавання інформації про військову придатність
    data['military']['fk_person'] = person.id
    military = MilitaryService(**data['military'])
    session.add(military)
    # Додавання інформації про сімю
    for arg in data['family']:
        arg['fk_person'] = person.id
        arg['birthday'] = arg['birthday'][0:10]
        family = Family(**arg)
        session.add(family)
    # Додавання інформації про досвід роботи
    for arg in data['workExp']:
        arg['fk_person'] = person.id
        experience = Experience(**arg)
        session.add(experience)
    session.commit()
    vacation_user(id_worker)
    return person.id


def candidate_to_worker_sql(_id, data, sid, card_number):
    """
    Прийняття кандидата на роботу
    :param _id: ід кандидата
    :param data: обєк з даними про кандидата
    :param sid: sid отриманий з АД
    :param card_number: отриманий при створенню користувача в 1с
    """
    session = Session()
    mail = data['AD']['givenName-En'] + '.' + data['AD']['snEn'] + '@busmarket.ua'
    id_dep = session.query(Department1c.id).filter(Department1c.name == data['department']).first()
    id_position = session.query(Position.id).filter(Position.name == data['position']).first()
    id_branch = session.query(Branch.id).filter(Branch.name == data['branch']).first()
    # photo = data['photo']
    # Добавляння фото
    # if photo != '':
    #     document = Document(name='фотографія', file_type='', file=photo.encode('utf-8'), type_='', fk_person=_id)
    #     db.session.add(document)
    data['person']['birthday'] = data['person']['birthday'][0:10]
    data['person']['type_'] = ''
    data['person']['date_of_issue'] = data['person']['date_of_issue'][0:10]
    data['worker']['started_to_work'] = data['worker']['started_to_work'][0:10]
    data['worker']['sid'] = sid
    data['worker']['fk_position'] = id_position[0]
    data['worker']['fk_branch'] = id_branch[0]
    data['worker']['fk_person'] = _id
    data['worker']['fk_department'] = id_dep[0]
    if data['permissions']['email'] == '1':
        data['person']['email'] = mail.lower()
        data['worker']['email'] = mail.lower()
    session.query(Person).filter_by(id=_id).update(data['person'])
    # створення працівника
    worker = Worker(**data['worker'])
    session.add(worker)
    session.flush()
    id_worker = worker.id
    # заповнення зарплати
    salary = Salary(salary=data['salary'], fk_position=id_position[0], fk_worker=id_worker)
    session.add(salary)
    session.commit()
    vacation_user(id_worker)
    return


def candidate_update(data, _id):
    """
    Оновлення даних кандидата
    :param data: обєкт з даними по кандидату
    :param _id: ід кандидата
    """
    session = Session()
    data['person']['birthday'] = data['person']['birthday'][0:10]
    data['person']['date_of_issue'] = data['person']['date_of_issue'][0:10]
    session.query(Person).filter_by(id=_id).update(data['person'])
    session.commit()


def update_worker(_id, data):
    """
    Оновлення даних працівника
    :param _id: ід пфіз особи
    :param data: обєк з даними працівника
    """
    session = Session()
    session.query(Person).filter_by(id=_id).update(data['person'])
    session.query(Worker).filter_by(fk_person=_id).update(data['worker'])
    session.commit()


def dismissed_to_worker_sql(_id, data, sid, card_number):
    """
    Провторне прийняття на роботу звільненого працівника
    :param _id: фіз особи
    :param data: обєкт з даними по фіз особі
    :param sid: отриманих з АД
    :param card_number: отиманий з 1с при створенні
    """
    # mail = data['givenName-En'] + '.' + data['snEn'] + '@busmarket.ua'
    id_dep = db.session.query(Department1c.id).filter(Department1c.name == data['departmentUa']).first()
    id_position = db.session.query(Position.id).filter(Position.name == data['titleUa']).first()
    id_branch = db.session.query(Branch.id).filter(Branch.name == data['company']).first()
    photo = data['photo']
    # Добавляння фото
    if photo != '':
        document = Document(name='фотографія', file_type='', file=photo.encode('utf-8'), type_='', fk_person=_id)
        db.session.add(document)
    db.session.query(Person).filter_by(id=_id).update(
        {"type_ ": 'worker', "name": data['givenNameUa'], "surname": data['snUa'], "middle_name": data['middlename'],
         "place_of_residence": data['address_residence'], "registration": data['registration'], "ipn": data['ipn'],
         "mobile_phone": data['phone'], "passport_id": data['pasNumber'], "date_of_issue": data['pasDate'][0:10],
         "issued_by": data['pasIssued'], "skype": data['pager'], "gender": data['gender'],
         "birthday": data['birthday']})
    # створення працівника
    worker = Worker(sid=sid, name_ua=data['givenNameUa'], name_ru=data['givenName'], name_en=data['givenName-En'],
                    surname_ua=data['snUa'], surname_ru=data['sn'], surname_en=data['snEn'],
                    middle_name_ua=data['middlename'], middle_name_ru=data['middlenameRu'], card_number=card_number,
                    skype=data['pager'], status='active', work_schedule=data['schedule'],
                    started_to_work=data['dateIn'][0:10], fk_position=id_position[0], fk_branch=id_branch[0],
                    fk_person=_id, fk_department=id_dep[0])
    db.session.add(worker)
    db.session.flush()
    id_worker = worker.id
    # заповнення зарплати
    salary = Salary(salary=data['salary'], fk_position=id_position[0], fk_worker=id_worker)
    db.session.add(salary)
    db.session.commit()
    vacation_user(id_worker)


def correction_of_collisions_sql(data):
    """
    Виправлення невідповідностей між базами АД,1с та SQL в SQL БД
    :param data: обєкт працввника
    """
    session = Session()
    _id = session.query(Worker.id, Worker.fk_person).filter(Worker.sid == data['c']['SID']).first()
    data['person']['birthday'] = data['person']['birthday'][0:10]
    session.query(Person).filter_by(id=_id[1]).update(data['person'])
    session.query(Worker).filter_by(id=_id[0]).update(data['worker'])
    session.query(Collision).filter(Collision.sid == data['c']['SID']).delete()
    session.commit()
