from datetime import datetime
import random
import string
from db import Session
from alchemybase import Person, Vacation, Worker
from marshmallow_schemas import VacationSchema, PersonSchema, WorkerSchema

def id_generator(size=10, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def vacation_user(_id):
    """
    Нарахування відпустки працівнику за діючий рік якщо він прийнятий на роботу цього ж року
    :param _id: ід працівника
    """
    session = Session()
    datenow = datetime.strftime(datetime.now(), "%Y-%m-%d")
    date2 = datetime.strptime(str(datenow), "%Y-%m-%d").date()
    result = session.query(Worker.id, Worker.started_to_work, Worker.finished_to_work).filter(
        Worker.status == 'active').filter(Worker.id == _id).first()
    date = str(result[1].year) + '-12-31'
    date1 = datetime.strptime(str(date), "%Y-%m-%d").date()
    if result[1].year == date1.year:
        if result[1].day < 10:
            s1 = 2
        elif result[1].day < 21:
            s1 = 1
        else:
            s1 = 0
        # кількість заробленої відпустки за цей рік
        count = s1 + 2 * (date1.month - result[1].month)
        vacation_new = Vacation(count=count, used=0, balance=count, year=date2.year, updated=date2,
                                fk_worker=result[0])
        session.add(vacation_new)
    session.commit()
    session.close()
    return count


def vacation():
    """
    Заповнення відпусти за поточний рік всім працівникам
    """
    session = Session()
    date2 = datetime.strftime(datetime.now(), "%Y-%m-%d")
    date1 = datetime.date(datetime.now())
    result = session.query(Worker.id, Worker.started_to_work, Worker.finished_to_work).filter(
        Worker.status == 'active').all()
    for arg in result:
        if date1.year != arg[1].year and not session.query(Vacation).filter(Vacation.year == date1.year).filter(
                Vacation.fk_worker == arg[0]).first():
            # Додати період +24 за поточний рік
            vacation_new = Vacation(count=24, used=0, balance=24, year=date1.year, updated=date2[0:10],
                                    fk_worker=arg[0])
            session.add(vacation_new)
            # нарахування відпустки якщо людина була прийнята на роботу цього року
        elif not session.query(Vacation).filter(Vacation.year == date1.year).filter(
                Vacation.fk_worker == arg[0]).first():
            vacation_user(arg[0])
    session.commit()
    session.close()


def vacation_release(_id, date):
    """
    Розрахунок залишку відпустки при звільненні
    :param _id: ід працівника
    :param date: дата звільнення 
    """
    session = Session()
    date1 = datetime.strptime(str(date), "%Y-%m-%d").date()
    id_w = session.query(Worker.id, Worker.started_to_work).filter_by(fk_person=_id).first()
    dd = datetime.strptime(str(id_w[1]), "%Y-%m-%d").date()
    records = session.query(Vacation).filter_by(fk_worker=id_w[0]).all()
    converter = VacationSchema(many=True, only=['count', 'used'])
    vacations = converter.dump(records).data
    vac_count = 0
    used = 0
    for arg in vacations:
        vac_count += arg['count']
        used += arg['used']
    # якщо прийнятий та звільнений тогож місяця
    if dd.month == date1.month and dd.year == date1.year:
        if date1.day - dd.day > 20:
            count = 2
        elif date1.day - dd.day > 10:
            count = 1
        else:
            count = 0
        response = count
    else:
        # рахуємо відпустки за ост місяць
        if date1.day > 20:
            s2 = 2
        elif date1.day > 9:
            s2 = 1
        else:
            s2 = 0
        # Якщо людина прийнята на роботу цього року
        if dd.year == date1.year:
            if dd.day < 10:
                s1 = 2
            elif dd.day < 21:
                s1 = 1
            else:
                s1 = 0
            # кількість заробленої відпустки за цей рік
            count = s1 + s2 + 2 * (date1.month - dd.month - 1)
            response = count
        else:
            # якщо людина прийнята на роботу в попередніх роках
            count = 2 * (date1.month - 1) + s2
            response = vac_count - 24 + count
    session.close()
    return response - used
