from db import Session
from alchemybase import Poll, Question, Variant, Statistics, Answer, Person, Document, MilitaryService, Language, \
    Family, Education, Experience, Recommendation, Priority
from marshmallow_schemas import PollSchema, QuestionSchema, VariantSchema
from sqlalchemy import func
from sqlalchemy.orm.session import make_transient


def poll_unpdate(_id):
    result = {}
    session = Session()
    records = session.query(Poll).filter_by(id=_id).first()
    converter = PollSchema(only=['id', 'description', 'name'])
    result = converter.dump(records).data
    question = session.query(Question).filter_by(fk_poll=_id).all()
    converter = QuestionSchema(many=True, only=['id', 'question', 'type_'])
    list_question = converter.dump(question).data
    for arg in list_question:
        records_answer = session.query(Variant).filter_by(fk_question=arg['id']).all()
        converter = VariantSchema(many=True, only=['text'])
        answer = converter.dump(records_answer).data
        variant = []
        for resp in answer:
            variant.append(resp['text'])
        arg['answers'] = variant
    result['questions'] = list_question
    session.close()
    return result


def get_poll_statistics(_id):
    session = Session()
    result = {}
    poll = session.query(Poll).filter(Poll.id == _id).first()
    if not poll:
        return False
    result['name'] = poll.name
    result['people'] = poll.total_count
    result['people_finish'] = poll.count_of_complete
    result['description'] = poll.description

    question = []
    questions = session.query(Question).filter(Question.fk_poll == _id).all()
    for q in questions:
        res = {}
        res['text'] = q.question
        res['type'] = q.type_
        variant = []
        if q.type_ == 'text':
            answers = session.query(Answer).filter(Answer.fk_question == q.id).all()  # FIRST?
            for a in answers:
                variant.append(a.answer)
        else:
            variants = session.query(Variant).filter(Variant.fk_question == q.id).all()
            for v in variants:
                answer = {}
                count = session.query(func.count(Answer.id)).filter(Answer.fk_question == q.id).filter(
                    Answer.answer == v.text).first()[0]
                answer['variant'] = v.text
                answer['count'] = count
                variant.append(answer)
        res['answers'] = variant
        question.append(res)
    result['question'] = question
    return result


def get_poll_statistics_by_dep(dep, _id):
    session = Session()
    result = {}
    poll = session.query(Poll).filter(Poll.id == _id).first()

    if not poll:
        return False

    total_count = 0
    count_of_complete = 0

    polls_in_dep = session.query(Statistics).filter(Statistics.fk_poll == _id).filter(
        Statistics.department == dep).all()
    for stat in polls_in_dep:
        total_count += stat.total_count
        count_of_complete += stat.count_of_complete

    result['name'] = poll.name
    result['people'] = total_count
    result['people_finish'] = count_of_complete
    result['description'] = poll.description

    question = []
    question_list = session.query(Question).filter(Question.fk_poll == _id).all()
    for q in question_list:
        res = {}
        res['text'] = q.question
        res['type'] = q.type_

        variant = []
        if q.type_ == 'text':
            answers = session.query(Answer).filter(Answer.fk_question == q.id).filter(Answer.department == dep).all()
            for a in answers:
                variant.append(a.answer)
        else:
            variants = session.query(Variant).filter(Variant.fk_question == q.id).all()
            for v in variants:
                answer = {}
                count = session.query(func.count(Answer.id)).filter(Answer.fk_question == q.id).filter(
                    Answer.answer == v.text).filter(Answer.department == dep).first()
                answer['variant'] = v.text
                answer['count'] = count[0]
                variant.append(answer)
        res['answers'] = variant
        question.append(res)
    result['question'] = question
    return result


def get_poll_statistics_by_city(city, _id):
    session = Session()
    result = {}
    poll = session.query(Poll).filter(Poll.id == _id).first()
    if not poll:
        return False
    total_count = 0
    count_of_complete = 0
    statistic_list = session.query(Statistics).filter(Statistics.fk_poll == _id).filter(Statistics.city == city).all()

    for s in statistic_list:
        total_count += s.total_count
        count_of_complete += s.count_of_complete

    result['name'] = poll.name
    result['people'] = total_count
    result['people_finish'] = count_of_complete
    result['description'] = poll.description

    question = []
    question_list = session.query(Question).filter(Question.fk_poll == _id).all()
    for q in question_list:
        res = {}
        res['text'] = q.name
        res['type'] = q.type_
        variant = []
        if q.type_ == 'text':
            answer_list = session.query(Answer).filter(Answer.fk_question == q.id).filter(Answer.city == city).all()
            for a in answer_list:
                variant.append(a.answer)
        else:
            variant_list = session.query(Variant).filter(Variant.fk_question == q.id).all()
            for v in variant_list:
                answer = {}
                count = session.query(func.count(Answer.id)).filter(Answer.fk_question == q.id).filter(
                    Answer.answer == v.text).filter(Answer.city == city).first()
                answer['variant'] = v.text
                answer['count'] = count[0]
                variant.append(answer)
        res['answers'] = variant
        question.append(res)
    result['question'] = question
    return result


def get_poll_statistics_by_dep_city(dep, city, _id):
    session = Session()
    result = {}
    poll = session.query(Poll).filter(Poll.id == _id).first()
    if not poll:
        return False

    total_count = 0
    count_of_complete = 0
    statistic_list = session.query(Statistics).filter(Statistics.fk_poll == _id).filter(
        Statistics.department == dep).all()

    for s in statistic_list:
        total_count += s.total_count
        count_of_complete += s.count_of_complete

    result['name'] = poll.name
    result['people'] = total_count
    result['people_finish'] = count_of_complete
    result['description'] = poll.description

    question = []
    question_list = session.query(Question).filter(Question.fk_poll == _id).all()
    for q in question_list:
        res = {}
        res['text'] = q.text
        res['type'] = q.type_
        variant = []
        if q.type_ == 'text':
            answer_list = session.query(Answer).filter(Answer.fk_question == q.id).filter(
                Answer.department == dep).filter(Answer.city == city).all()
            for a in answer_list:
                variant.append(a.answer)
        else:
            variant_list = session.query(Variant).filter(Variant.fk_question == q.id).all()
            for v in variant_list:
                answer = {}
                count = session.query(func.count(Answer.id)).filter(Answer.fk_question == q.id).filter(
                    Answer.answer == v.text).filter(Answer.department == dep).filter(Answer.city == city).first()
                answer['variant'] = v.text
                answer['count'] = count[0]
                variant.append(answer)
        res['answers'] = variant
        question.append(res)
    result['question'] = question
    return result

def save_anketa_individual(data):
    session = Session()
    # data['person']['birthday'] = current_date(data['person']['birthday'])
    data['person']['birthday'] = data['person']['birthday'][0:10]
    if data['person']['date_of_issue'] != '':
        # data['person']['date_of_issue'] = current_date(data['person']['date_of_issue'])
        data['person']['date_of_issue'] = data['person']['date_of_issue'][0:10]
    else:
        data['person'].pop('date_of_issue')
    person = Person(**data['person'])
    session.add(person)
    session.flush()
    # photo = data['photo']
    # if photo != '':
    #     document = Document(name='фотографія', file_type='', file=photo.encode('utf-8'), type_='', fk_person=person.id)
    #     db.session.add(document)
    data['military']['fk_person'] = person.id
    military = MilitaryService(**data['military'])
    session.add(military)
    for arg in data['language']:
        arg['fk_person'] = person.id
        language = Language(**arg)
        session.add(language)
    for arg in data['family']:
        arg['fk_person'] = person.id
        if arg['birthday'] != '':
            # arg['birthday'] = current_date(arg['birthday'])
            arg['birthday'] = arg['birthday'][0:10]
        else:
            arg.pop('birthday')
        family = Family(**arg)
        session.add(family)
    for arg in data['education']:
        arg['fk_person'] = person.id
        education = Education(**arg)
        session.add(education)
    for arg in data['workExp']:
        arg['fk_person'] = person.id
        workExp = Experience(**arg)
        session.add(workExp)
    for arg in data['recomendations']:
        arg['fk_person'] = person.id
        recomendations = Recommendation(**arg)
        session.add(recomendations)
    data['priority']['fk_person'] = person.id
    priority = Priority(**data['priority'])
    session.add(priority)
    for arg in data['other'].keys():
        try:
            id_ = int(arg)
            if type(data['other'][arg]) == dict:
                for res in data['other'][arg].values():
                    answer = Answer(answer=res, fk_question=id_, fk_person=person.id)
                    session.add(answer)
            elif data['other'][arg] != '':
                answer = Answer(answer=data['other'][arg], fk_question=id_, fk_person=person.id)
                session.add(answer)
        except:
            pass
    session.commit()
    return person.id

def anketa_info(_id):
    session = Session()
    records = session.query(Poll).filter_by(id=_id).first()
    converter = PollSchema(only=['id', 'description', 'name'])
    result = converter.dump(records).data
    question = session.query(Question).filter_by(fk_poll=_id).all()
    converter = QuestionSchema(many=True, only=['block', 'final', 'id', 'required', 'question', 'type_', 'value'])
    list_question = converter.dump(question).data
    for arg in list_question:
        records_answer = session.query(Variant).filter_by(fk_question=arg['id']).all()
        converter = VariantSchema(many=True, only=['text'])
        answer = converter.dump(records_answer).data
        variant = []
        for resp in answer:
            variant.append(resp['text'])
        arg['answers'] = variant
    result['question'] = list_question
    session.close()
    return result


def poll_save(data):
    session = Session()
    if data['id'] != '':
        id_poll = data['id']
        session.query(Poll).filter_by(id=id_poll).delete()
        poll = Poll(id=id_poll, name=data['name'], count_of_complete=0, total_count=0, status='develop',
                    description=data['description'])
        session.add(poll)
    else:
        poll = Poll(name=data['name'], count_of_complete=0, total_count=0, status='develop',
                    description=data['description'])
        session.add(poll)
        session.flush()
        id_poll = poll.id
    for arg in data['questions']:
        print(arg)
        question = Question(question=arg['question'], type_=arg['type_'], fk_poll=id_poll)
        session.add(question)
        session.flush()
        id_question = question.id
        for res in arg['answers']:
            variant = Variant(text=res, fk_question=id_question)
            session.add(variant)
    session.commit()
    session.close()
    return id_poll


def copy_db(_id):
    session = Session()
    obj = session.query(Poll).filter_by(id=_id).first()
    id_poll = obj.id
    session.expunge(obj)
    obj.id = None
    obj.name = '(Копія) ' + obj.name
    obj.status = 'develop'
    obj.count_of_complete = 0
    obj.total_count = 0
    make_transient(obj)
    session.add(obj)
    session.flush()
    question = session.query(Question).filter_by(fk_poll=id_poll).all()
    for arg in question:
        session.expunge(arg)
        question_id = arg.id
        arg.id = None
        arg.fk_poll = obj.id
        make_transient(arg)
        session.add(arg)
        varaint = session.query(Variant).filter_by(fk_question=question_id).all()
        for res in varaint:
            session.expunge(res)
            res.id = None
            res.fk_question = arg.id
            make_transient(res)
            session.add(res)
    session.commit()
    session.close()
