from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from datetime import datetime

Base = declarative_base()


class WorkSchedule(Base):
    """
    Робочий графік працівників підтягнутий з бази 1с
    """
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True)
    schedule = Column(String(100), nullable=False)

    def __repr__(self):
        return "{id=%s, schedule='%s'}" % (self.id, self.schedule)


class EducationType(Base):
    """
    Тип освіти(вища, неповна вища,..) підтягнутий з бази 1с
    """
    __tablename__ = 'educationtypes'
    id = Column(Integer, primary_key=True)
    code = Column(String(20))
    name = Column(String(250))

    def __repr__(self):
        return "{id=%s, code='%s', name='%s'}" % (self.id, self.code, self.name)


class EducationInstitution(Base):
    """
    Навчальні заклади підтягнуті з бази 1с
    """
    __tablename__ = 'institutions'
    id = Column(Integer, primary_key=True)
    code = Column(String(20))
    name = Column(String(250))

    def __repr__(self):
        return "{id=%s, code='%s', name='%s'}" % (self.id, self.code, self.name)


class Specialty(Base):
    """"
    Спеціальності підтягнуті з бази 1с
    """
    __tablename__ = 'specialities'
    id = Column(Integer, primary_key=True)
    code = Column(String(20))
    name = Column(String(250))

    def __repr__(self):
        return "{id=%s, code='%s', name='%s'}" % (self.id, self.code, self.name)


class DismissalArticle(Base):
    """
    Статті звільнення працівника підтягнуті з бази 1с
    """
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    code = Column(String(20))
    name = Column(String(250))

    def __repr__(self):
        return "{id=%s, code='%s', name='%s'}" % (self.id, self.code, self.name)


class DismissalReason(Base):
    """
    Причини звільнення працівника підтягнуті з бази 1с
    """
    __tablename__ = 'reasons'
    id = Column(Integer, primary_key=True)
    code = Column(String(20))
    name = Column(String(250))

    def __repr__(self):
        return "{id=%s, code='%s', name='%s'}" % (self.id, self.code, self.name)


class DepartmentAD(Base):
    """
    Робочі відділи підтягнуті з ActiveDirectory
    """
    __tablename__ = 'departmentsad'
    id = Column(Integer, primary_key=True)
    department = Column(String(256))

    def __repr__(self):
        return "{id=%s, department='%s'}" % (self.id, self.department)


class Collision(Base):
    """
    Невідповідності в даних працівника між базами 1с та ActiveDirectory
    """
    __tablename__ = 'collisions'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), default=None)
    surname = Column(String(150), default=None)
    position = Column(String(150), default=None, doc='Посада')
    department = Column(String(100), default=None)
    sid = Column(String(100), default=None, doc='id в ActiveDirectory')
    fixed = Column(String(100), default=False,
                   doc='Помітка про виправлення. Якщо True, значить невідповідності усунено')
    description = Column(String(256), default='')

    def __repr__(self):
        return "{id=%s, name='%s', surname='%s', position='%s', department='%s', sid='%s', fixed='%s', description='%s'}" % \
               (self.id, self.name, self.surname, self.position, self.department, self.sid, self.fixed,
                self.description)


class Position(Base):
    """
    Посади працівників підтягнуті з бази 1с
    """
    __tablename__ = 'positions'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    name_en = Column(String(100))
    position_code = Column(String(20))

    def __repr__(self):
        return "{id=%s, name='%s', name_en='%s', position_code='%s'}" % (
            self.id, self.name, self.name_en, self.position_code)


class Department1c(Base):
    """
    Робочі відділи з бази 1c
    """
    __tablename__ = 'departments1c'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    name_en = Column(String(150))
    department_code = Column(String(20))
    status = Column(String(20),default='active')

    def __repr__(self):
        return "{id=%s, name='%s', name_en='%s', department_code='%s', status='%s'}" % (
            self.id, self.name, self.name_en, self.department_code, self.status)


class Region(Base):
    """
    Регіони з ActiveDirectory
    """
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    name_en = Column(String(100))
    country = Column(String(100))
    country_en = Column(String(100))

    def __repr__(self):
        return "{id=%s, name='%s', name_en='%s', country='%s', country_en='%s'}" % \
               (self.id, self.name, self.name_en, self.country, self.country_en)


class Poll(Base):
    """
    Опитування. Використовуються для опитування нових працівників і як анонімні опитування
    """
    __tablename__ = 'polls'
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    created = Column(DateTime, default=datetime.now)
    count_of_complete = Column(Integer, doc='К-ть завершених опитування')
    total_count = Column(Integer, doc='Загальна к-ть надісланих опитувань')
    status = Column(String(100))
    description = Column(Text, default=None)

    def __repr__(self):
        return "{id=%s, name='%s', created='%s', count_of_complete='%s', total_count='%s', status='%s', description='%s'}" % \
               (self.id, self.name, self.created, self.count_of_complete, self.total_count, self.status,
                self.description)


class Question(Base):
    """
    Запитання для опитувань
    """
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    question = Column(Text, doc='Формулювання питання')
    type_ = Column(String(50), doc='Тип запитання: текст, checkbox, radiobutton')
    block = Column(Integer, default=None, doc='номер блока в анкеті, в якому буде розміщене питання')
    required = Column(Boolean, default=False, doc="Маркер обов'язковості запитання")
    value = Column(Text, default=None, doc='Містить відповідь на запитання передане з фронта')
    final = Column(Boolean, default=False,
                   doc='Використовуєтсья для додаванян повторного поля. Наприклад, ще одна освіта, робота, сімя')
    fk_poll = Column(Integer, ForeignKey(Poll.id))
    poll = relationship(Poll, backref=backref('questions', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, question='%s', type_='%s', block='%s', require='%s', value='%s', final='%s'," \
               "fk_polls='%s'}" % (self.id, self.question, self.type_, self.block, self.required,
                                   self.value, self.final, self.fk_poll)


class Variant(Base):
    """
    Варіанти відповідей до запитань, якщо тип запитання checkbox або radiobutton
    """
    __tablename__ = 'variants'
    id = Column(Integer, primary_key=True)
    text = Column(Text)

    fk_question = Column(Integer, ForeignKey(Question.id))
    question = relationship(Question, backref=backref('variants', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, text='%s', fk_question='%s'}" % (self.id, self.text, self.fk_question)


class Statistics(Base):
    """
    Таблиця статистики для опитування
    """
    __tablename__ = 'statistics'
    id = Column(Integer, primary_key=True)
    total_count = Column(Integer, default=0, doc='Загальна к-ть розісланих')
    count_of_complete = Column(Integer, default=0, doc='К-ть перегнлянутих')
    department = Column(String(250), default='', doc='Департамент')
    city = Column(String(250), doc='Місто')

    fk_poll = Column(Integer, ForeignKey(Poll.id))
    poll = relationship(Poll, backref=backref('statistics', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, total_count='%s', count_of_complete='%s', department='%s', city='%s', fk_poll='%s'}" % (
            self.id, self.total_count, self.count_of_complete, self.department, self.city, self.fk_poll)


class Password(Base):
    """
    Паролі для опитувань
    """
    __tablename__ = 'passwords'
    id = Column(Integer, primary_key=True)
    password = Column(String(10), nullable=False)
    department = Column(String(250), default='')
    city = Column(String(250), default='')

    fk_poll = Column(Integer, ForeignKey(Poll.id))
    poll = relationship(Poll, backref=backref('passwords', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, password='%s', department='%s', city='%s', fk_poll='%s'}" % (
            self.id, self.password, self.department, self.city, self.fk_poll)


class Person(Base):
    """
    Таблиця фізичної особи
    """
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    surname = Column(String(100))
    middle_name = Column(String(80), default=None)
    birthday = Column(DateTime, default=None)
    marital_status = Column(String(50), default=None, doc='Сімейний стан')
    place_of_residence = Column(String(256), default=None, doc='Місце проживання')
    registration = Column(String(150), default=None, doc='Місце прописки')
    ipn = Column(String(50), default=None, doc='Індивідуальнйи податковий номер')
    mobile_phone = Column(String(20), default=None)
    home_phone = Column(String(20), default=None)
    email = Column(String(100))
    skype = Column(String(100), default=None)
    gender = Column(String(256), default=None)
    passport_id = Column(String(10), default=None, doc='Серія номер паспорта')
    date_of_issue = Column(DateTime, default=None, doc='Дата видачі паспорту')
    issued_by = Column(String(250), default=None, doc='Ким видано паспорт')
    type_ = Column(String(50), default=None, doc='Тип: кандидат, активний, відхилено')
    department = Column(String(150), default=None, doc='Департамент. Тільки для кандидатів')
    city = Column(String(150), default=None, doc='Місто. Тільки для кандидатів')
    position = Column(String(250), default=None, doc='Посада. Тільки для кандидатів')

    fk_poll = Column(Integer, ForeignKey(Poll.id), default=None)
    poll = relationship(Poll, backref=backref('persons', uselist=True, cascade='delete,all'))

    # TODO add to repr department, city, position
    def __repr__(self):
        return "{id=%s, name='%s', surname='%s', middle_name='%s', birthday='%s', marital_status='%s', " \
               "place_of_residence='%s', registration='%s', ipn='%s', mobile_phone='%s', home_phone='%s', email='%s', " \
               "skype='%s', gender='%s', passport_id='%s', date_of_issue='%s', issued_by='%s', fk_poll='%s'}" % \
               (self.id, self.name, self.surname, self.middle_name, self.birthday, self.marital_status,
                self.place_of_residence, self.registration, self.ipn, self.mobile_phone, self.home_phone,
                self.email,
                self.skype, self.gender, self.passport_id, self.date_of_issue, self.issued_by, self.fk_poll)


class Answer(Base):
    """
    Таблиця з відповідями до опитувань
    """
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    answer = Column(Text)
    password = Column(String(20), default=None, doc='Пароль для опитування')
    department = Column(String(250), default='')
    city = Column(String(250), default='')

    fk_person = Column(Integer, ForeignKey(Person.id))
    fk_question = Column(Integer, ForeignKey(Question.id))
    person = relationship(Person, backref=backref('answers', uselist=True, cascade='delete,all'))
    question = relationship(Question, backref=backref('answers', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, answer='%s', password='%s', department='%s', city='%s', fk_person='%s', fk_question='%s'}" % (
            self.id, self.answer, self.password, self.department, self.city, self.fk_person, self.fk_question)


class Language(Base):
    """
    Таблиця знання мов
    """
    __tablename__ = 'languages'
    id = Column(Integer, primary_key=True)
    language = Column(String(150))
    knowledge_level = Column(String(100))

    fk_person = Column(Integer, ForeignKey(Person.id))
    person = relationship(Person, backref=backref('languages', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, language='%s', possession='%s', fk_individual='%s'}" % (
            self.id, self.language, self.knowledge_level, self.fk_person)


class MilitaryService(Base):
    """
    Таблиця по придатність до військової служби
    """
    __tablename__ = 'militaryservices'
    id = Column(Integer, primary_key=True)
    military_suitability = Column(String(150), doc='Військова придатність')
    rank = Column(String(100), doc='Військове знання')
    corps = Column(String(100), doc='Рід військ')
    years = Column(String(100), doc='Роки служби')

    fk_person = Column(Integer, ForeignKey(Person.id))
    person = relationship(Person, backref=backref('militaryservices', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, military_suitability='%s', rank='%s', corps='%s', years='%s', fk_person='%s'}" % \
               (self.id, self.military_suitability, self.rank, self.corps, self.years, self.fk_person)


class Priority(Base):
    """
    Таблиця з пріоритетами для кандидатів. Кандидату потрібно розставити твердження  в порядку важливості для нього
    """
    # TODO від 1 до 10
    __tablename__ = 'priorities'
    id = Column(Integer, primary_key=True)
    priority1 = Column(Integer)
    priority2 = Column(Integer)
    priority3 = Column(Integer)
    priority4 = Column(Integer)
    priority5 = Column(Integer)
    priority6 = Column(Integer)
    priority7 = Column(Integer)
    priority8 = Column(Integer)
    priority9 = Column(Integer)
    priority10 = Column(Integer)

    fk_person = Column(Integer, ForeignKey(Person.id))
    person = relationship(Person, backref=backref('priorities', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, priority1='%s', priority2='%s', priority3='%s', priority4='%s', priority5='%s', " \
               "priority6='%s',priority7='%s', priority8='%s', priority9='%s', priority10='%s', fk_individual='%s'}" % \
               (self.id, self.priority1, self.priority2, self.priority3, self.priority4, self.priority5, self.priority6,
                self.priority7, self.priority8, self.priority9, self.priority10, self.fk_person)


class Family(Base):
    """
    Відомості про сімю
    """
    __tablename__ = 'families'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    surname = Column(String(50))
    birthday = Column(DateTime)  # Дата народження?
    type_ = Column(String(50), doc='Тип: дружина, дитина..')
    workplace = Column(String(150), default=None, doc='Місце роботи')
    position = Column(String(150), default=None, doc='Посада')

    fk_person = Column(Integer, ForeignKey(Person.id))
    person = relationship(Person, backref=backref('families', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{'id': %s, 'name': '%s', 'surname': '%s', 'birthday': '%s', 'type': '%s', 'workplace': '%s', 'position': '%s', 'fk_person': '%s'}" % \
               (
                   self.id, self.name, self.surname, self.birthday, self.type_, self.workplace, self.position,
                   self.fk_person)


class Document(Base):
    """
    Таблиця з документами
    """
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), doc='Назва документу')
    file_type = Column(String(100), doc='тип файлу')
    file = Column(BLOB, doc='Файл з документом')
    created = Column(DateTime, default=datetime.now)
    status = Column(String(50), default='active')
    type_ = Column(String(150))

    fk_person = Column(Integer, ForeignKey(Person.id))
    person = relationship(Person, backref=backref('documents', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, name='%s', create_date='%s', status='%s', type='%s', fk_individual='%s'}" % \
               (self.id, self.name, self.created, self.status, self.type_,
                self.fk_person)


class Experience(Base):
    """
    Досвід роботи
    """
    __tablename__ = 'experience'
    id = Column(Integer, primary_key=True)
    years = Column(String(50), default=None, doc='Роки роботи')
    workplace = Column(String(250), default=None, doc='Місце роботи')
    position = Column(String(200), default=None, doc='Посада')
    duties = Column(Text, default=None, doc='Обовязки')
    salary = Column(String(20), default=None)

    dismissal_reason = Column(String(20), default=None, doc='Причина звільнення')

    fk_person = Column(Integer, ForeignKey(Person.id))
    person = relationship(Person, backref=backref('experience', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, years='%s', workplace='%s', position='%s', duties='%s', salary='%s', dismissal_reason='%s', fk_person='%s'}" % \
               (self.id, self.years, self.workplace, self.position, self.duties, self.salary, self.dismissal_reason,
                self.fk_person)


class Recommendation(Base):
    """
    Дані про людину з попередньої роботи, як може надати рекомендацію по працівнику
    """
    __tablename__ = 'recomendations'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), doc='Імя та прізвище людини, яка може надати рекомендацію')
    position = Column(String(250), doc='Посада людини, яка може надати рекомендацію')
    organization = Column(String(200), doc='Назва організації')
    phone_number = Column(String(30), doc='Номер телефона людини, яка може надати рекомендацію')

    fk_person = Column(Integer, ForeignKey(Person.id))
    person = relationship(Person, backref=backref('recommendations', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, name='%s', position='%s', organization='%s', phone_number='%s', fk_individual='%s'}" % \
               (self.id, self.name, self.position, self.organization, self.phone_number, self.fk_person)


class Education(Base):
    """
    Таблиця з відомостями про освіту
    """
    __tablename__ = 'education'
    id = Column(Integer, primary_key=True)
    institution_name = Column(String(250), doc='Назва навчального закладу')
    education_type = Column(String(150), doc='Тип освіти')
    diploma = Column(String(100), doc='Номер диплома')
    date_of_graduation = Column(String(50), doc='Дата закінчення')
    specialty = Column(String(200), doc='Спеціальність')
    qualification = Column(String(200), doc='Кваліфікаційний рівень')
    form_of_training = Column(String(100), doc='Форма навчання')
    main_specialty = Column(String(150), doc='Досвід роботи за основною спецальністю')
    years_of_experience = Column(String(150), doc='Роки досвіду роботи за спецальністю')
    faculty = Column(String(150), doc='Факультет')

    fk_person = Column(Integer, ForeignKey(Person.id))
    person = relationship(Person, backref=backref('education', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, institution_name='%s', education_type='%s', diploma='%s', date_of_graduation='%s', specialty='%s'," \
               "qualification='%s',form_of_training='%s', main_specialty='%s',years_of_experience='%s',faculty='%s',fk_individual='%s'}" % \
               (self.id, self.institution_name, self.education_type, self.diploma, self.date_of_graduation,
                self.specialty,
                self.qualification, self.form_of_training, self.main_specialty, self.years_of_experience, self.faculty,
                self.fk_person)


class Note(Base):
    """
    Таблиця з нотатками
    """
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    text = Column(Text)
    created = Column(DateTime, default=datetime.now)
    type_ = Column(String(150))
    public = Column(Boolean, default=True,
                    doc='Маркер загальної відображуваності нотатки')
    id_person = Column(Integer, default=None)

    fk_author = Column(Integer, ForeignKey(Person.id))
    person = relationship(Person, backref=backref('notes', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, name='%s', text='%s', created='%s', type='%s', public='%s',id_person='%s', fk_author='%s'}" % \
               (
                   self.id, self.name, self.text, self.created, self.type_, self.public, self.id_person,
                   self.fk_author)


class City(Base):
    """
    Таблиця з містами
    """
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    name_en = Column(String(100))

    fk_region = Column(Integer, ForeignKey(Region.id))
    region = relationship(Region, backref=backref('cities', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, name='%s', name_en='%s', fk_region='%s'}" % (self.id, self.name, self.name_en, self.fk_region)


class Branch(Base):
    """
    Таблиця з філіалами
    """
    __tablename__ = 'branches'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    name_en = Column(String(100))
    zip_code = Column(Integer)
    address_ua = Column(String(100))
    address_en = Column(String(100))
    address_ru = Column(String(100))
    status = Column(String(20), default='active')

    fk_city = Column(Integer, ForeignKey(City.id))
    city = relationship(City, backref=backref('branches', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, name='%s', name_en='%s', zip_code='%s', address_ua='%s', address_en='%s', address_ru='%s',  fk_city='%s'}" % \
               (self.id, self.name, self.name_en, self.zip_code, self.address_ua, self.address_en, self.address_ru,
                self.fk_city)


class Worker(Base):
    """
    Таблиця з працівниками
    """
    __tablename__ = 'workers'
    id = Column(Integer, primary_key=True)
    sid = Column(String(100))
    name_ua = Column(String(100))
    name_ru = Column(String(100))
    name_en = Column(String(100))
    surname_ua = Column(String(100))
    surname_ru = Column(String(100))
    surname_en = Column(String(100))
    middle_name_ua = Column(String(100), default=None)
    middle_name_ru = Column(String(100), default=None)
    card_number = Column(String(30), default=None, doc='Номер картки працівникав в 1с')
    skype = Column(String(100), default=None)
    ip_phone = Column(String(100), default=None)
    email = Column(String(100))
    status = Column(String(100), default='active', doc='Статус працівника: активний, звільнений')
    work_schedule = Column(String(150), default=None, doc='Робочий графік')
    started_to_work = Column(DateTime, default=None, doc='Дата початку роботи')
    finished_to_work = Column(DateTime, default=None, doc='Дата закінчення роботи')
    dismissal_article = Column(String(250), default='', doc='Стаття звільнення')
    dismissal_reason = Column(String(250), default='', doc='Причина звільнення')
    dismissal_comment = Column(Text, doc='Коментар до звільнення')
    mainorg = Column(String(256), default=None, doc='Основна організація на яку прийнятий працівник')
    additionalorg = Column(String(256), default=None, doc='Додаткова організація на яку прийнятий працівник')
    duties = Column(Text, default=None)
    manager = Column(String(100), default='', doc='Лінійний керівник')
    confirmation_level = Column(String(100), default='', doc='Рівень погодження (відпустки)')

    fk_position = Column(Integer, ForeignKey(Position.id))
    fk_branch = Column(Integer, ForeignKey(Branch.id))
    fk_person = Column(Integer, ForeignKey(Person.id))
    fk_department = Column(Integer, ForeignKey(Department1c.id))
    position = relationship(Position, backref=backref('workers', uselist=True, cascade='delete,all'))
    branch = relationship(Branch, backref=backref('workers', uselist=True, cascade='delete,all'))
    person = relationship(Person, backref=backref('workers', uselist=True, cascade='delete,all'))
    department = relationship(Department1c, backref=backref('workers', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, sid='%s', name_en='%s', name_ua='%s', name_ru='%s', surname_en='%s',surname_ru='%s', surname_ua='%s', " \
               "card_number='%s', middle_name_ua='%s', middle_name_ru='%s', skype='%s', ip_phone='%s', email='%s', status='%s', " \
               "work_schedule='%s', started_to_work='%s', finished_to_work='%s', dismissal_article='%s', dismissal_reason='%s', dismissal_comment='%s', duties='%s',fk_person='%s'}" % \
               (
                   self.id, self.sid, self.name_en, self.name_ua, self.name_ru, self.surname_en, self.surname_ru,
                   self.surname_ua,
                   self.card_number, self.middle_name_ua, self.middle_name_ru, self.skype, self.ip_phone,
                   self.email,
                   self.status,
                   self.work_schedule, self.started_to_work, self.finished_to_work, self.dismissal_article,
                   self.dismissal_reason, self.dismissal_comment,self.duties,
                   self.fk_person)


class Salary(Base):
    """
    Таблиця з зарплатами
    """
    __tablename__ = 'salary'
    id = Column(Integer, primary_key=True)
    salary = Column(Float, default=0, doc='Зарплатня')
    start_date = Column(DateTime, default=None, doc='З якої дати була така зарплатня')
    end_date = Column(DateTime, default=None, doc='До якої дати була така зарплатня')

    fk_position = Column(Integer, ForeignKey(Position.id))
    fk_worker = Column(Integer, ForeignKey(Worker.id))
    position = relationship(Position, backref=backref('salary', uselist=True, cascade='delete,all'))
    worker = relationship(Worker, backref=backref('salary', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, salary='%s', start_date='%s', end_date='%s', fk_workers='%s'}" % \
               (self.id, self.salary, self.start_date, self.end_date, self.fk_worker)


class Vacation(Base):
    """
    Таблиця нарахування та використання відпусток працівників за певний рік
    """
    __tablename__ = 'vacations'
    id = Column(Integer, primary_key=True)
    count = Column(Integer, default=0, doc='Розмір нарахованої відпустки')
    used = Column(Integer, default=0, doc='Розмір використаної відпутки')
    balance = Column(Integer, doc='Різниця між нарахованим та використаним розмірами відпустки')
    year = Column(Integer, doc='Рік за який проводилось нарахування')
    updated = Column(DateTime, default=None, doc='Дата останнього оновлення ')

    fk_worker = Column(Integer, ForeignKey(Worker.id))
    worker = relationship(Worker, backref=backref('vacations', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, count='%s', used='%s', saldo='%s', year='%s',updated='%s', fk_workers='%s'}" % \
               (self.id, self.count, self.used, self.balance, self.year, self.updated, self.fk_worker)


class UsedVacation(Base):
    """
    Таблиця з відпустками працівників з зазначеними датою початку, кількістю днів та роком.
    """
    __tablename__ = 'vacationperiods'
    id = Column(Integer, primary_key=True)
    start_date = Column(DateTime, default=None, doc='Дата початку відпустки')
    end_date = Column(DateTime, default=None, doc='Дата кінця відпустки')
    count = Column(Integer, default=0, doc='К-ть календарних днів відпустки')
    year = Column(Integer, doc='Рік, за який надаєтсья відпустка')
    file = Column(BLOB, doc='Файл з фотографією')
    downloaded = Column(Boolean, default=False, doc='Маркер того, чи була завантажена фотографія')
    filename = Column(Text, doc='Імя файлу з фотографією')
    status = Column(String(20), default='confirmed')
    comments = Column(Text)

    fk_vacation = Column(Integer, ForeignKey(Vacation.id))
    vacation = relationship(Vacation, backref=backref('vacationperiods', uselist=True, cascade='delete,all'))

    def __repr__(self):
        return "{id=%s, start_date='%s', end_date='%s', count='%s', year='%s',downloaded='%s', filename='%s', fk_vacation='%s'}" % \
               (self.id, self.start_date, self.end_date, self.count, self.year,  self.downloaded,
                self.filename,
                self.fk_vacation)
