from ldap3 import Server, Connection, ALL, NONE, SCHEMA, DSA
from ldap3.core.exceptions import LDAPBindError, LDAPSocketSendError
from ldap3 import MODIFY_REPLACE
from db_utils import *
from config import *
from _1c_utils import load_users
import json
from alchemybase import Education, Experience, Person, City, Region, Branch, DepartmentAD, Worker, Department1c, \
    Position, Salary, Document
from marshmallow_schemas import EducationSchema, ExperienceSchema
from db import Session
import base64
import logging
from flask import current_app
from ldap3 import Tls, Server, Connection, ALL
import OpenSSL.crypto
from _ssl import CERT_REQUIRED, PROTOCOL_TLSv1_2

log = logging.getLogger()
log.setLevel(logging.DEBUG)

P_KEY_PATH = "private_key.pem"
CERT_KEY_PATH = "cert_key.pem"
CERT_PATH = "ca_cert.b64"


def _pfx_to_pem(pfx_path, pfx_password):
    """Decrypts the .pfx file to be used with requests. """
    pfx = open(pfx_path, 'rb').read()
    p12 = OpenSSL.crypto.load_pkcs12(pfx, pfx_password)

    with open(P_KEY_PATH, "wb") as fp:
        fp.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, p12.get_privatekey()))

    with open(CERT_KEY_PATH, "wb") as fp:
        fp.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate()))

    ca = p12.get_ca_certificates()

    with open(CERT_PATH, "wb") as fp:
        if ca is not None:
            for cert in ca:
                fp.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert))


def _get_connection(host, username, password):
    tls = Tls(local_private_key_file=P_KEY_PATH, local_certificate_file=CERT_KEY_PATH,
              ca_certs_file=CERT_PATH, validate=CERT_REQUIRED, version=PROTOCOL_TLSv1_2)

    server = Server(host, port=636, use_ssl=True, tls=tls, get_info=ALL)

    cxn = Connection(server=server, version=3, user=username, password=password, client_strategy='RESTARTABLE')
    cxn.start_tls()
    cxn.bind()
    return cxn


def get_ldaps_connection(host, username, password, pfx_path="hr.pfx", pfx_password=PFX_PASSWORD):
    _pfx_to_pem(pfx_path, pfx_password)
    cxn = _get_connection(host, username, password)
    return cxn


# ad = get_ldaps_connection('DC1.busmarket.ua', DC_USERNAME, DC_PASSWORD)


server = Server(DC_SERVER, use_ssl=True, get_info=ALL)
# ad = Connection(server, client_strategy='ASYNC', auto_bind=False, user=DC_USERNAME, password=DC_PASSWORD, pool_size=10)

ad = Connection(server, auto_bind=False, user=DC_USERNAME, password=DC_PASSWORD, pool_size=10,  client_strategy='RESTARTABLE')

def authenticate(login, password):
    try:
        # ad_ = get_ldaps_connection("DC1.busmarket.ua", login, password)
        ad_ = Connection(server, auto_bind=True, user=login, password=password, pool_size=1)
        ad_.bind(read_server_info=False)
    except (LDAPBindError, LDAPSocketSendError):
        return False
    return True


def load_users_from_ad():
    res = ad.search(search_base='DC=busmarket,DC=ua',
                    search_filter="	(&(objectCategory=person)(objectClass=user))",
                    attributes=['mail', 'telephoneNumber', 'sn', 'cn', 'givenName', 'displayName', 'department',
                                'mobile', 'givenName-En', 'givenNameUa', 'cityUa', 'departmentEn',
                                'ipPhone', 'isDeleted', 'userAccountControl', 'l', 'ManagedBy', 'Name', 'CanonicalName',
                                'givenName-En', 'snEn', 'givenNameUa', 'snUa', 'streetAddress',
                                'streetAddressCompany', 'streetAddressCompanyRu', 'co', 'title', 'titleEn', 'titleUa',
                                'departmentEn', 'departmentUa',
                                'company', 'thumbnailPhoto',
                                'companyEn', 'pager', 'st', 'streetAddressCompanyUa', 'streetAddressUa', 'stUa',
                                'postalCode', 'streetAddress', 'street', 'objectSid']
                    )
    return res


def process_ad_response(response, users_list, conditions):
    for entry in response:
        if 'attributes' not in entry:
            continue
        attributes = entry['attributes']
        if 'userAccountControl' in attributes:
            r = True
            for attribute, condition, true_false in conditions:
                r = r and ((attributes[attribute] == condition) == true_false)
            if r:
                users_list.append(dict(attributes))


def load_from_1c(arg, status):
    """
    Заповнення базу mysql з 1с працівниками
    :param arg: обєкт працівника з 1с
    :param status: active/dissmised
    """
    session = Session()
    dep = session.query(Department1c.id).filter(Department1c.name == arg['department']).first()
    if not dep:
        id_dep = 1
    else:
        id_dep = dep[0]
    id_position = session.query(Position.id).filter(Position.name == arg['position']).first()
    if 'Львів' in arg['department']:
        id_branch = 6
    elif 'Київ' in arg['department']:
        id_branch = 2
    elif 'Хмельницьк' in arg['department']:
        id_branch = 7
    elif 'Чернівц' in arg['department']:
        id_branch = 8
    else:
        id_branch = 1
    person = Person(name=arg['name'], surname=arg['surname'], middle_name=arg['middlename'],
                    birthday=arg['birthday'][0:10], marital_status=arg['married'],
                    place_of_residence=arg['address_of_residence'], registration=arg['place_of_residence'],
                    ipn=arg['IPN'], mobile_phone=arg['phone'], gender=arg['gender'])
    session.add(person)
    session.flush()
    worker = Worker(sid=arg['SID'], name_ua=arg['name'], surname_ua=arg['surname'],
                    middle_name_ua=arg['middlename'], card_number=arg['personnel_number'], status=status,
                    work_schedule=arg['schedule'], started_to_work=arg['startdate'][0:10],
                    finished_to_work=arg['enddate'][0:10], fk_position=id_position[0], fk_branch=id_branch,
                    fk_person=person.id, fk_department=id_dep)
    session.add(worker)
    session.flush()
    salary = Salary(salary=arg['salary'], fk_position=id_position[0], fk_worker=worker.id)
    session.add(salary)

    if arg['passport'] != []:
        session.query(Person).filter_by(id=person.id).update(
            {"passport_id": arg['passport'][0]['doc_series'] + arg['passport'][0]['doc_number'],
             "date_of_issue": arg['passport'][0]['doc_date'][0:10],
             "issued_by": arg['passport'][0]['doc_issuedby']})
    if arg['education'] != []:
        for res in arg['education']:
            education = Education(institution_name=res['institution'], education_type=res['type_education'],
                                  specialty=res['specialty'], faculty=res['faculty'], fk_person=person.id)
            session.add(education)
    session.commit()
    session.close()


def update_from_1c(arg, status, _id):
    """
    Оновлення бази mysql з 1с працівниками
    :param arg: обєкт працівника з 1с
    :param status: active/dissmised
    _Id: фiз особи
    """
    session = Session()
    dep = session.query(Department1c.id).filter(Department1c.name == arg['department']).first()
    if not dep:
        id_dep = 1
    else:
        id_dep = dep[0]
    id_position = session.query(Position.id).filter(Position.name == arg['position']).first()
    if 'Львів' in arg['department']:
        id_branch = 6
    elif 'Київ' in arg['department']:
        id_branch = 2
    elif 'Хмельницьк' in arg['department']:
        id_branch = 7
    elif 'Чернівц' in arg['department']:
        id_branch = 8
    else:
        id_branch = 1
    session.query(Person).filter_by(id=_id).update(
        {"name": arg['name'], "surname": arg['surname'], "middle_name": arg['middlename'],
         "birthday": arg['birthday'][0:10], "marital_status": arg['married'],
         "place_of_residence": arg['address_of_residence'], "registration": arg['place_of_residence'],
         "ipn": arg['IPN'], "mobile_phone": arg['phone'], "gender": arg['gender']})
    # session.query(Worker).filter_by(fk_person=_id).update(
    #     {"name_ua": arg['name'], "surname_ua": arg['surname'], "middle_name_ua": arg['middlename'],
    #      "card_number": arg['personnel_number'], "status": status, "work_schedule": arg['schedule'],
    #      "started_to_work": arg['startdate'][0:10], "finished_to_work": arg['enddate'][0:10],
    #      "fk_position": id_position[0], "fk_branch": id_branch, "fk_department": id_dep})
    # id_worker = session.query(Worker.id).filter(Worker.fk_person == _id).first()
    # session.query(Salary).filter_by(fk_worker=id_worker[0]).update(
    #     {"salary": arg['salary'], "fk_position": id_position[0]})
    # if arg['passport'] != []:
    #     session.query(Person).filter_by(id=_id).update(
    #         {"passport_id": arg['passport'][0]['doc_series'] + arg['passport'][0]['doc_number'],
    #          "date_of_issue": arg['passport'][0]['doc_date'][0:10],
    #          "issued_by": arg['passport'][0]['doc_issuedby']})
    session.commit()
    session.close()


def city_list():
    """
    Заповнення міста тарегіону в БД
    """
    users_list = []
    if load_users_from_ad():
        process_ad_response(ad.response, users_list, (
            ('userAccountControl', [], False),
            ('cityUa', [], False)
        ))
    session = Session()
    for arg in users_list:
        if not session.query(City).filter(City.name == arg['cityUa']).all():
            region = Region(name=arg['stUa'], name_en=arg['st'], country='Україна', country_en='Ukraine')
            session.add(region)
            session.flush()
            city = City(name=arg['cityUa'], name_en=arg['l'], fk_region=region.id)
            session.add(city)
    session.commit()
    session.close()


def branch_list():
    """
    Заповнення філіалу в БД
    """
    users_list = []
    if load_users_from_ad():
        process_ad_response(ad.response, users_list, (
            ('userAccountControl', [], False),
            ('company', [], False)
        ))
        session = Session()
        for arg in users_list:
            if not session.query(Branch).filter(Branch.name == arg['company']).all():
                fk_city = session.query(City.id).filter(City.name == arg['cityUa']).first()
                branch = Branch(name=arg['company'], name_en=arg['companyEn'], zip_code=arg['postalCode'],
                                address_ua=arg['streetAddressUa'], address_en=arg['street'],
                                address_ru=arg['streetAddress'], fk_city=fk_city[0])
                session.add(branch)
        session.commit()
        session.close()


def department_poll():
    """
    Заповнення відділів з АД в БД
    """
    users_list = []
    if load_users_from_ad():
        process_ad_response(ad.response, users_list, (
            ('userAccountControl', [], False),
            ('departmentUa', [], False)
        ))
        session = Session()
        for arg in users_list:
            if not session.query(DepartmentAD).filter(DepartmentAD.department == arg['departmentUa']).all():
                department = DepartmentAD(department=arg['departmentUa'])
                session.add(department)
        session.commit()
        session.close()


def from_dep(mail):
    """
    Повертає відділ до якого належить працівник за даним email
    :param mail: email працівника
    """
    users_list = []
    if load_users_from_ad():
        process_ad_response(ad.response, users_list, (
            ('userAccountControl', [], False),
            ('departmentUa', [], False),
            ('mail', mail, True)
        ))
    return users_list


def candidate_insert(arg):
    """
    Заповнює освіту та дозвід роботи кандидату, для відображання в загальній інформації
    :param arg: обєкт кандидат
    """
    session = Session()
    all_exp = session.query(Experience).join(Person, Person.id == Experience.fk_person) \
        .filter(Person.id == arg['id']).all()
    converter = ExperienceSchema(many=True, exclude=['person'])
    exp = converter.dump(all_exp).data
    all_edu = session.query(Education).join(Person, Person.id == Education.fk_person) \
        .filter(Person.id == arg['id']).all()
    converter = EducationSchema(many=True, exclude=['person'])
    edu = converter.dump(all_edu).data
    arg['education'] = edu
    arg['experience'] = exp
    session.close()
    return arg


def dismissed():
    """
    Заповнення в БД звільнених працівників
    """
    _1c = json.loads(load_users())
    session = Session()
    for arg in _1c['data']:
        if arg['dismissed'] and not session.query(Worker).filter(Worker.name_ua == arg['name']).filter(
                Worker.surname_ua == arg['surname']).filter(Worker.middle_name_ua == arg['middlename']).first():
            load_from_1c(arg, 'dismissed')
    session.close()


def active_worker():
    """
    Заповнення в БД працівників
    """
    _1c = json.loads(load_users())
    session = Session()
    for arg in _1c['data']:
        if not session.query(Worker).filter(Worker.sid == arg['SID']).first() and not arg['dismissed'] \
                and arg['SID'] != '':
            load_from_1c(arg, 'active')
    session.close()


def active_worker_without_sid():
    """
    Заповнення в БД працівників в яких немає sid
    """
    _1c = json.loads(load_users())
    session = Session()
    for arg in _1c['data']:
        if not arg['dismissed'] and arg['SID'] == '' and not session.query(Worker).filter(
                Worker.name_ua == arg['name']).filter(Worker.surname_ua == arg['surname']).filter(
            Worker.middle_name_ua == arg['middlename']).first():
            load_from_1c(arg, 'active')
    session.close()


def update_user_db_1c():
    """
    оновлення даних з 1с
    """
    _1c = json.loads(load_users())
    session = Session()
    for arg in _1c['data']:
        worker = session.query(Worker).filter(Worker.sid == arg['SID']).first()
        if worker and arg['SID'] != '':
            if arg['dismissed']:
                status = 'dismissed'
            else:
                status = 'active'
            update_from_1c(arg, status, worker.fk_person)
    session.close()


def update_user_db_ad():
    """
    Доповнення БД даними з АД
    """
    session = Session()
    records = session.query(Worker.sid, Worker.fk_person).filter(Worker.sid != '').all()
    for arg in records:
        user = []
        res = ad.search(search_base=BASE_DN,
                        search_filter="(objectSid={sid})".format(sid=arg[0]),
                        attributes=['mail', 'sn', 'givenName', 'pager', 'thumbnailPhoto',
                                    'mobile', 'givenName-En', 'givenNameUa', 'cityUa',
                                    'ipPhone', 'l', 'givenName-En', 'snEn', 'givenNameUa', 'snUa', 'objectSid']
                        )

        if res:
            for entry in ad.response:
                if 'dn' in entry:
                    user.append(dict(entry['attributes']))
        if user:
            if user[0]['thumbnailPhoto']:
                byte_string = user[0]['thumbnailPhoto']
                encoded_data = base64.b64encode(byte_string)
                photo = Document(name='фотографія', file_type='', file=encoded_data, type_='', fk_person=arg[1])
                session.add(photo)
            for resp in user[0]:
                if not user[0][resp]:
                    user[0][resp] = ''
            session.query(Person).filter_by(id=arg[1]).update({"email": user[0]['mail'], "skype": user[0]['pager']})
            session.query(Worker).filter_by(fk_person=arg[1]).update(
                {"name_en": user[0]['givenName-En'], "name_ru": user[0]['givenName'], "surname_en": user[0]['snEn'],
                 "surname_ru": user[0]['sn'], "skype": user[0]['pager'], "ip_phone": user[0]['ipPhone'],
                 "email": user[0]['mail']})
    session.commit()
    session.close()


def update_user_AD(data, sid):
    user = []
    res = ad.search(search_base=BASE_DN,
                    search_filter="(objectSid={sid})".format(sid=sid),
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
            if 'attributes' not in entry:
                continue
            attributes = entry['attributes']
            USER_DN = entry['dn']
            user.append(dict(attributes))

            # Редагування даних в AD
            ad.modify(USER_DN,
                      {
                          'sn': [(MODIFY_REPLACE, [data['sn']])],
                          'givenName': [(MODIFY_REPLACE, [data['givenName']])],
                          'company': [(MODIFY_REPLACE, [data['company']])],
                          'ipPhone': [(MODIFY_REPLACE, [data['ipPhone']])],
                          'mail': [(MODIFY_REPLACE, [data['mail']])],
                          'mobile': [(MODIFY_REPLACE, [data['mobile']])],
                          'pager': [(MODIFY_REPLACE, [data['pager']])],
                          'stUa': [(MODIFY_REPLACE, [data['stUa']])],
                          'snUa': [(MODIFY_REPLACE, [data['snUa']])],
                          'cityUa': [(MODIFY_REPLACE, [data['cityUa']])],
                          'snEn': [(MODIFY_REPLACE, [data['snEn']])],
                          'givenNameUa': [(MODIFY_REPLACE, [data['givenNameUa']])],
                          'givenName-En': [(MODIFY_REPLACE, [data['givenName-En']])],
                          'postalCode': [(MODIFY_REPLACE, [data['postalCode']])],
                          'streetAddressUa': [(MODIFY_REPLACE, [data['streetAddressUa']])]
                      })


def add_new_user_to_AD(data):
    # створення нової OU
    ress = ad.add('OU=OtherUser,OU=BMGROUP,DC=busmarket,DC=ua', 'organizationalUnit')
    current_app.logger.info('створення OU=OtherUser - {}\n'.format(ress))
    if ad.closed:
        ad.open()
    if not ad.bound:
        ad.bind(read_server_info=True)
    session = Session()
    branch = session.query(Branch.name_en, Branch.zip_code, Branch.address_ru, Branch.address_ua,
                           Branch.address_en).filter(Branch.name == data['company']).first()
    region = session.query(Region.name, Region.name_en).join(City, City.fk_region == Region.id).filter(
        City.name == data['cityUa']).first()
    city = session.query(City.name_en).filter(City.name == data['cityUa']).first()
    if data['phone'] == '':
        mobile = ' '
    else:
        mobile = data['phone']
    if data['pager'] == '':
        skype = ' '
    else:
        skype = data['pager']
    response = {
        'givenName': data['givenName'],
        'givenName-En': data['givenName-En'],
        'givenNameUa': data['givenNameUa'],
        'sn': data['sn'],
        'snEn': data['snEn'],
        'snUa': data['snUa'],
        'companyEn': branch[0],
        'company': data['company'],
        'cityUa': data['cityUa'],
        'l': city[0],
        'coUa': 'Україна',
        'coRu': 'Украина',
        'coEn': 'Ukraine',
        'postalCode': str(branch[1]),
        'streetAddress': branch[2],
        'streetAddressUa': branch[3],
        'street': branch[4],
        'st': region[1],
        'stUa': region[0],
        'pager': skype,
        'name': data['givenName'] + ' ' + data['sn'],
        'displayName': data['givenName'] + ' ' + data['sn'],
        'mobile': mobile
    }
    session.close()
    CN = "CN={sname} {name},OU=OtherUser,OU=BMGROUP,DC=busmarket,DC=ua".format(sname=data['sn'], name=data['givenName'])
    response_user = ad.add(CN, 'User', response)
    # print(ad.add(CN, 'User', response))
    current_app.logger.info('створення користувача в AD - {}\n'.format(response_user))
    # print(res)
    # if res:
    #     send_info_mail(response, data['titleUa'], data['departmentUa'])
    user = []
    res = ad.search(search_base=CN,
                    search_filter="(objectCategory=person)",
                    attributes=['mail', 'mobile', 'objectSid']
                    )
    if res:
        for entry in ad.response:
            if 'attributes' not in entry:
                continue
            attributes = entry['attributes']
            user.append(dict(attributes))
    current_app.logger.info('sid - {}'.format(user[0]['objectSid']))
    return user[0]['objectSid']


def update_user_AD_info(data, sid):
    user = []
    res = ad.search(search_base=BASE_DN,
                    search_filter="(objectSid={sid})".format(sid=sid),
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
            if 'attributes' not in entry:
                continue
            attributes = entry['attributes']
            USER_DN = entry['dn']
            user.append(dict(attributes))

            # Редагування даних в AD
            ad.modify(USER_DN,
                      {
                          'ipPhone': [(MODIFY_REPLACE, [data['ip_phone']])],
                          'mail': [(MODIFY_REPLACE, [data['email']])],
                          'mobile': [(MODIFY_REPLACE, [data['phone']])],
                          'pager': [(MODIFY_REPLACE, [data['skype']])],
                          'snUa': [(MODIFY_REPLACE, [data['sname']])],
                          'snEn': [(MODIFY_REPLACE, [data['sname_en']])],
                          'givenNameUa': [(MODIFY_REPLACE, [data['name']])],
                          'givenName-En': [(MODIFY_REPLACE, [data['name_en']])],
                      })
