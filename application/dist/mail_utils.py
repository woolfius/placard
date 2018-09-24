import logging
from flask import current_app
from config import mail_server, mail_port, mail_username, mail_password, Authorization_password
import smtplib
from smtplib import SMTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTPServerDisconnected, SMTPRecipientsRefused, SMTPAuthenticationError
from db_utils import id_generator
from db import Session
from alchemybase import Password
import requests

log = logging.getLogger()
log.setLevel(logging.DEBUG)


def send_sms(res, _id):
    data = []
    for arg in res:
        password = id_generator()
        temp = {}
        temp.setdefault('template', 'hr_portal')
        temp.setdefault('sms', True)
        temp.setdefault('phone_number', arg)
        body = {}
        body.setdefault('password', password)
        temp.setdefault('body', body)
        data.append(temp)
        headers = {'Authorization': Authorization_password}
        respons = requests.post('https://mailingservice.busmarket.ua/create_task_post', json=data, headers=headers)
        session = Session()
        passrords = Password(password=password, fk_poll=_id)
        session.add(passrords)
        session.close()


def send_mail(mail, password):
    """
    Відправка листа з паролем
    """
    mail_to = mail
    themsg = MIMEMultipart()
    themsg['Subject'] = Header('Пройдіть анонімне опитування', 'utf-8')
    html = """<head>
              <meta charset="UTF-8">
              </head>
              <h1>Доброго дня!</h1>
              <p>Пропонуємо вам пройти анонімне опитування нашої компанії. Силка для проходження опитування нижче</p>
              <p><a href='https://polls.busmarket.ua/auth'>Анонімне опитування</a></p>
              <p>Пароль для входу {password}</p>
              """.format(password=password)
    message = MIMEText(html, 'html')
    themsg.attach(message)
    themsg = themsg.as_string()

    server = smtplib.SMTP(mail_server, mail_port, timeout=60)
    server.starttls()
    try:
        server.login(mail_username, mail_password)
        server.sendmail(mail_username, mail_to, themsg)
        server.quit()
        current_app.logger.info('email успішно відправлено.\n')
    except SMTPException as error:
        current_app.logger.warning('Не вдалось відправити листа.\n%s' % str(error))
        return False
    return True


def send_info_mail(data, position, department):
    themsg = MIMEMultipart()
    themsg['Subject'] = Header('Створено нового користувача', 'utf-8')
    html = """<head>
              <meta charset="UTF-8">
              </head>
              <h3>Перевір правильність заповнених даних та дозаповни необхідні поля</h3>
              <p>Було створено нового користувача {name} {sname} </p>
              <p>Місто - {city}, філіал {branch} </p>
              <p>На посаду - {position} в департамент {department}</p>
              <h5>Заповненні наступні поля</h5>
              <ul>
            <li>'companyEn':{companyEn},</li>
            <li>'company':{company},</li>
            <li>'cityUa':{cityUa},</li>
            <li>'l': {l},</li>
            <li>'name': {name1},</li>
            <li>'displayName':{displayName},</li>
            <li>'givenName':{givenName},</li>
            <li>'givenName-En': {givenNameEn},</li>
            <li>'givenNameUa': {givenNameUa},</li>
            <li>'sn': {sn},</li>
            <li>'snEn': {snEn},</li>
            <li>'snUa': {snUa},</li>
            <li>'coUa':'Україна',</li>
            <li>'coRu':'Украина',</li>
            <li>'coEn':'Ukraine',</li>
            <li>'mail': {mail},</li>
            <li>'mobile': {mobile},</li>
            <li>'postalCode': {postalCode},</li>
            <li>'streetAddress': {streetAddress},</li>
            <li>'streetAddressUa':{streetAddressUa},</li>
            <li>'street':{street},</li>
            <li>'st': {st},</li>
            <li>'stUa': {stUa}</li>
            </ul>
              """.format(name=data['givenNameUa'], sname=data['snUa'], city=data['cityUa'], branch=data['company'],
                         position=position, department=department, companyEn=data['companyEn'], company=data['company'],
                         cityUa=data['cityUa'], l=data['l'], name1=data['name'], displayName=data['displayName'],
                         givenName=data['givenName'], givenNameEn=data['givenName-En'], givenNameUa=data['givenNameUa'],
                         sn=data['sn'], snEn=data['snEn'], snUa=data['snUa'],
                         mail=data['mail'], mobile=data['mobile'], postalCode=data['postalCode'],
                         streetAddress=data['streetAddress'], streetAddressUa=data['streetAddressUa'],
                         street=data['street'], st=data['st'], stUa=data['stUa'])
    message = MIMEText(html, 'html')
    themsg.attach(message)
    themsg = themsg.as_string()

    server = smtplib.SMTP(mail_server, mail_port, timeout=20)
    server.starttls()
    try:
        server.login(mail_username, mail_password)
        server.sendmail(mail_username, 'ivan.zakrevskyi@busmarket.ua', themsg)
        server.quit()
        current_app.logger.info('email про створення користувача успішно відправлено.\n')
    except SMTPException as error:
        current_app.logger.warning('Не вдалось відправити листа про створення користувача.\n%s' % str(error))
        return False
    return True
