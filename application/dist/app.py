from flask import Flask, jsonify

from flask_login import LoginManager
from ldap3.core.exceptions import LDAPSocketSendError
from _1c_utils import *

import json

from login_model import User

from datetime import datetime
from ldap_utils import *
from db_utils import *
from config import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from time import sleep
import threading

from werkzeug.contrib.fixers import ProxyFix
from db import Session
from alchemybase import Note, WorkSchedule, DepartmentAD, Position, Department1c, Region, City, Branch, EducationType, \
    EducationInstitution, Specialty, DismissalArticle, DismissalReason, Collision, Poll, Question, Variant, Statistics, \
    Password, Person, Answer, Language, MilitaryService, Priority, Family, Document, Experience, Recommendation, \
    Education, Worker, Salary, Vacation, UsedVacation
from marshmallow_schemas import WorkScheduleSchema, EducationTypeSchema, EducationInstitutionSchema, SpecialtySchema, \
    DismissalArticleSchema, DismissalReasonSchema, DepartmentADSchema, CollisionSchema, PositionSchema, \
    Department1cSchema, RegionSchema, PollSchema, QuestionSchema, VariantSchema, StatisticsSchema, PasswordSchema, \
    PersonSchema, AnswerSchema, LanguageSchema, MilitaryServiceSchema, PrioritySchema, FamilySchema, DocumentSchema, \
    ExperienceSchema, RecommendationSchema, EducationSchema, NoteSchema, CitySchema, BranchSchema, WorkerSchema, \
    SalarySchema, VacationSchema, UsedVacationSchema

app = Flask(__name__)
app.config.from_object('config')
app.wsgi_app = ProxyFix(app.wsgi_app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "other.login_view"
login_manager.login_message = "Будь ласка пройдіть авторизацію для доступу до ресурсу!"
login_manager.login_message_category = "info"

time_start1 = {'07:23'}

# Base = declarative_base()
# engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, SERVER, PORT, DB_NAME))
# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)
# session = Session()


class ThreadingExample(object):
    def __init__(self, interval=1):
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()  # Start the execution

    def run(self):
        while True:
            d = datetime.today()
            time_x = d.strftime('%H:%M')
            if time_x in time_start1:
                if ad.closed:
                    ad.open()
                if not ad.bound:
                    ad.bind(read_server_info=True)
                # sync_db()
                # vacation()
                sleep(60)

            sleep(self.interval)


def sync_db():
    """
    Функція для синхронізації між базами 1с, АД та Mysql(Визначення невідповідностей полів працівника в базах)
    """
    session = Session()
    get_GetEducationType()
    get_GetInstitution()
    # get_Specialty()
    get_dismissal_articles()
    get_dismissal_reasons()
    get_GetPosition()
    get_GetDepartment()
    # department_poll()
    # city_list()
    # branch_list()
    # active_worker()
    # dismissed()
    # active_worker_without_sid()
    # update_user_db_ad()
    update_user_db_1c()
    session.query(Collision).filter(Collision.id > 0).delete()
    ad_list = []
    if load_users_from_ad():
        process_ad_response(ad.response, ad_list, (
            ('userAccountControl', [], False),
            ('departmentUa', [], False)
        ))
    all_records = session.query(Worker).join(Person, Person.id == Worker.fk_person).join(Position,
                                                                                         Position.id == Worker.fk_position,
                                                                                         isouter=True).join(
        Department1c, Department1c.id == Worker.fk_department, isouter=True).all()
    converter = WorkerSchema(many=True,
                             only=['sid', 'name_ua', 'name_en', 'surname_en', 'card_number', 'status', 'skype', 'email',
                                   'started_to_work', 'finished_to_work', 'middle_name_ua', 'work_schedule',
                                   'person.passport_id', 'person.date_of_issue', 'person.issued_by',
                                   'ip_phone', 'surname_ua', 'person.mobile_phone', 'person.id', 'person.ipn',
                                   'person.birthday', 'person.home_phone', 'position.name', 'department.name',
                                   'person.place_of_residence', 'person.registration', 'person.marital_status',
                                   'surname_ru', 'name_ru'])
    mysql_list = converter.dump(all_records).data
    _1c = json.loads(load_users())
    result = []

    for user in _1c['data']:
        data = {}
        if user['dismissed'] == False and user['SID'] == "":
            data.setdefault('user', user)
            data.setdefault('description',
                            'По користувачу не може бути проведена синхронізація, оскільки користувача в 1с немає SID')
            result.append(data)
        elif user['dismissed'] == False and user['SID'] != "":
            for res in mysql_list:
                if res['sid'] == user['SID']:
                    check = False
                    count = 0
                    for arg in ad_list:
                        if user['SID'] == arg['objectSid']:
                            check = True
                            if (arg['givenNameUa'] != res['name_ua']) or (arg['givenNameUa'] != user['name']):
                                count += 1
                            if (arg['snUa'] != res['surname_ua']) or (arg['snUa'] != user['surname']):
                                count += 1
                            if (arg['mobile'] != res['person']['mobile_phone']) or (arg['mobile'] != user['phone']):
                                count += 1
                            if arg['snEn'] != res['surname_en']:
                                count += 1
                            if res['name_en'] != arg['givenName-En']:
                                count += 1
                            if res['surname_ru'] != arg['sn']:
                                count += 1
                            if res['name_ru'] != arg['givenName']:
                                count += 1
                            if res['skype'] != arg['pager']:
                                count += 1
                            if res['ip_phone'] != arg['ipPhone']:
                                count += 1
                            if res['email'] != arg['mail']:
                                count += 1
                    if (res['person']['place_of_residence'] != user['address_of_residence']):
                        count += 1
                    if (res['person']['registration'] != user['place_of_residence']):
                        count += 1
                    if user['IPN'] != res['person']['ipn']:
                        count += 1
                    if user['middlename'] != res['middle_name_ua']:
                        count += 1
                    if check == False:
                        if user['name'] != res['name_ua']:
                            count += 1
                        if user['surname'] != res['surname_ua']:
                            count += 1
                        if user['phone'] != res['person']['mobile_phone']:
                            count += 1
                    if count > 0:
                        data.setdefault('user', user)
                        data.setdefault('description', count)
                        result.append(data)
    for arg in result:
        collision = Collision(name=arg['user']['name'], surname=arg['user']['surname'],
                              position=arg['user']['position'], department=arg['user']['department'],
                              sid=arg['user']['SID'], description=arg['description'])
        session.add(collision)
    session.commit()
    session.close()


@app.before_request
def check_ad_connection():
    if ad.closed:
        ad.open()
    if not ad.bound:
        ad.bind(read_server_info=True)


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.errorhandler(LDAPSocketSendError)
def ldap_socket_error():
    return jsonify()


example = ThreadingExample()

if __name__ == "__main__":
    app.run(debug=True)
