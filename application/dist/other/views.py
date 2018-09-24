import base64
import io
from datetime import datetime

from flask import Blueprint, request, url_for, flash, render_template, jsonify, send_file
from flask_login import login_required, login_user, logout_user
from werkzeug.utils import redirect

from alchemybase import Document, Position, Worker, Person, func
from app import app
from db import Session
from forms import LoginForm
from ldap_utils import update_user_db_1c
from login_model import User
from marshmallow_schemas import PositionSchema, WorkerSchema

other = Blueprint('other', __name__)


@other.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')


@other.route('/files', methods=['GET', 'POST'])
def upload_file():
    """
    Збереження файлів в БД.
    """
    MAX_FILE_SIZE = 4024 * 4024 + 1
    if request.method == 'POST':
        file = request.files["file"]
        print(request.files)
        if bool(file.filename):
            file_bytes = file.read(MAX_FILE_SIZE)
            gif_str = base64.b64encode(file_bytes)
            id_ = request.form['id']
            print(id_)
            url = request.form['redirect']
            print(url)


            type = request.form['type']
            date1 = datetime.strftime(datetime.now(), "%Y.%m.%d")
            name = request.form['name']
            print(name)
            session = Session()
            documents = Document(name=name, file_type=file.mimetype, file=gif_str, type_=type, fk_person=id_)
            session.add(documents)
            session.commit()
            session.close()
            return redirect('/#!' +url + '#' + request.form['part'])
    return 'ok'

@other.route('/photo', methods=['GET', 'POST'])
def upload_photo():
    """
    Збереження файлів в БД.
    """
    MAX_FILE_SIZE = 4024 * 4024 + 1
    if request.method == 'POST':
        file = request.files["file"]
        print(file)
        if bool(file.filename):
            file_bytes = file.read(MAX_FILE_SIZE)
            gif_str = base64.b64encode(file_bytes)
            id_ = request.form['id']
            print(id_)
            type = 'photo'
            date1 = datetime.strftime(datetime.now(), "%Y.%m.%d")
            name = 'фотографія'
            session = Session()
            documents = Document(name=name, file_type=file.mimetype, file=gif_str, type_=type, fk_person=id_)
            session.add(documents)
            session.commit()
            session.close()
            print('hello')
            return redirect('/#!/employees/new/')
            # return 'ok'
    return 'ok'


@other.route('/auth', methods=['GET', 'POST'])
def login_view():
    """
    Авторизація користувача.
    """
    form = LoginForm()
    if form.validate_on_submit():
        login, password = form.login.data, form.password.data
        user = User(login)
        if user.check_password(password):
            login_user(user)
            app.logger.info('[ACCESS GRANTED] Користувач [%s] успішно авторизивоний' % login)
            return redirect(url_for('other.index'))
        else:
            app.logger.info('[ACCESS DENIED] Не правильний логін [%s] або пароль [%s]' % (login, '*' * len(password)))
            flash('Не вірний логін або пароль!', category='warning')

    return render_template('login.html', form=form)


@other.route('/sign_out')
@login_required
def drop_session():
    """
    Вихід із системи користувача. В групу Other
    """
    logout_user()
    return redirect(url_for('other.login_view'))


@other.route('/api/position', methods=['GET'])
@login_required
def api_position():
    """
    Повертає список всіх посад компанії.
    """
    session = Session()
    all_records = session.query(Position).all()
    converter = PositionSchema(many=True)
    res = converter.dump(all_records).data
    result = []
    for arg in res:
        result.append(arg['name'])
    session.close()
    return jsonify(result)


@other.route('/api/birthday/', methods=['GET'])
def api_birthday_mail():
    """
    Повертає сьогоднішніх іменинників. В групу Other
    """
    session = Session()
    date1 = datetime.strftime(datetime.now(), "%Y-%m-%d")
    birthday = session.query(Worker.email) \
        .join(Person, Person.id == Worker.fk_person) \
        .filter(func.day(Person.birthday) == func.day(date1)) \
        .filter(func.month(Person.birthday) == func.month(date1)).all()
    converter = WorkerSchema(many=True, only=['email'])
    result = converter.dump(birthday).data
    return jsonify(result)


@other.route('/get_photo/<_id>', methods=['POST', 'GET'])
@login_required
def get_photo_id(_id):
    """
    Повертає фотографію фіз особи, якщо немає фотографії повертає фото за замовчуванням.
    :param id: id фіз особи
    :return:
    """
    session = Session()
    response = session.query(Document.file).filter_by(fk_person=_id).filter_by(status='active').filter_by(
        name='фотографія').first()

    if response == None:
        avatar = b'iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAMAAADDpiTIAAADAFBMVEUAAAD///////////+/v7/MzMzV1dXb29vf39/j4+Pm5ubo6OjV1dXY2Njb29vd3d3f39/h4eHj4+Pk5OTZ2dnb29vc3Nze3t7f39/g4ODi4uLj4+Pb29vc3Nzd3d3e3t7f39/g4ODh4eHb29vc3Nzd3d3d3d3e3t7f39/g4ODh4eHb29vc3Nzd3d3e3t7e3t7f39/g4ODg4ODc3Nzd3d3d3d3e3t7f39/f39/g4ODc3Nzc3Nzd3d3e3t7e3t7f39/f39/g4ODc3Nzd3d3d3d3e3t7e3t7f39/f39/g4ODd3d3d3d3d3d3e3t7e3t7f39/f39/g4ODd3d3d3d3e3t7e3t7e3t7f39/f39/d3d3d3d3d3d3e3t7e3t7e3t7f39/f39/d3d3d3d3e3t7e3t7e3t7f39/f39/f39/d3d3d3d3e3t7e3t7e3t7f39/f39/f39/d3d3d3d3e3t7e3t7e3t7f39/f39/d3d3d3d3e3t7e3t7e3t7e3t7f39/f39/d3d3d3d3e3t7e3t7e3t7e3t7f39/f39/d3d3d3d3e3t7e3t7e3t7e3t7f39/d3d3d3d3e3t7e3t7e3t7e3t7e3t7f39/d3d3d3d3e3t7e3t7e3t7e3t7f39/f39/d3d3e3t7e3t7e3t7e3t7e3t7f39/f39/d3d3e3t7e3t7e3t7e3t7e3t7f39/d3d3d3d3e3t7e3t7e3t7e3t7e3t7f39/d3d3e3t7e3t7e3t7e3t7e3t7e3t7f39/d3d3e3t7e3t7e3t7e3t7e3t7e3t7f39/e3t7e3t7e3t7e3t7e3t7e3t7f39/d3d3e3t7e3t7e3t7e3t7e3t7e3t7f39/d3d3e3t7e3t7e3t7e3t7e3t7e3t7f39/e3t7e3t7e3t7e3t7e3t7e3t7e3t7d3d3e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t7e3t6HNBeAAAAA/3RSTlMAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1O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'
        gif_str = base64.b64decode(avatar)
        return send_file(io.BytesIO(gif_str), mimetype='image/jpg')
    gif_str = base64.b64decode(response[0])
    session.close()
    return send_file(io.BytesIO(gif_str), mimetype='image/jpg')

@other.route('/files_compress/<_id>', methods=['POST'])
def upload_file_compress(_id):
    """
    Збереження файлів в БД.
    """
    data = request.json
    session = Session()
    session.query(Document).filter(Document.fk_person == _id).filter(
        Document.name == 'фотографія').update({'status': 'not active'})
    sid = session.query(Worker.sid).filter(Worker.fk_person == _id).first()
    documents = Document(name='фотографія', file_type=data['mimetype'], file=str.encode(data['base']), type_=data['type'],
                         fk_person=_id)
    session.add(documents)
    session.commit()
    return 'ok'

@other.route('/api/start', methods=['GET'])
def start():
    """
    Функція для заповнення первинними даними інформації з 1с та АД, якщо Mysql БД пуста.
    """
    # get_GetEducationType()
    # get_GetInstitution()
    # get_Specialty()
    # get_dismissal_articles()
    # get_dismissal_reasons()
    # get_GetPosition()
    # get_GetDepartment()
    # city_list()
    # branch_list()
    # active_worker()
    # dismissed()
    # active_worker_without_sid()
    # update_user_db_ad()
    update_user_db_1c()
    # department_poll()
    # vacation()
    # from_dep('marian.reverenda@busmarket.ua')
    return 'ok'
