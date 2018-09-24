from marshmallow import fields, post_dump, post_load
from marshmallow_sqlalchemy import ModelSchema, ModelConverter
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.sqltypes import NullType
from pprint import pprint

from alchemybase import Base, WorkSchedule, EducationType, EducationInstitution, Specialty, DismissalArticle, \
    DismissalReason, DepartmentAD, Collision, Position, Department1c, Region, Poll, Question, Variant, Statistics, \
    Password, Person, Answer, Language, MilitaryService, Priority, Family, Document, Experience, Recommendation, \
    Education, Note, City, Branch, Worker, Salary, Vacation, UsedVacation


class SQLAlchemyUtilsConverter(ModelConverter):
    SQLA_TYPE_MAPPING = dict(list(ModelConverter.SQLA_TYPE_MAPPING.items()) + [(NullType, fields.Raw)])


class WorkScheduleSchema(ModelSchema):
    class Meta:
        model = WorkSchedule
        model_converter = SQLAlchemyUtilsConverter


class EducationTypeSchema(ModelSchema):
    class Meta:
        model = EducationType
        model_converter = SQLAlchemyUtilsConverter


class EducationInstitutionSchema(ModelSchema):
    class Meta:
        model = EducationInstitution
        model_converter = SQLAlchemyUtilsConverter


class SpecialtySchema(ModelSchema):
    class Meta:
        model = Specialty
        model_converter = SQLAlchemyUtilsConverter


class DismissalArticleSchema(ModelSchema):
    class Meta:
        model = DismissalArticle
        model_converter = SQLAlchemyUtilsConverter


class DismissalReasonSchema(ModelSchema):
    class Meta:
        model = DismissalReason
        model_converter = SQLAlchemyUtilsConverter


class DepartmentADSchema(ModelSchema):
    class Meta:
        model = DepartmentAD
        model_converter = SQLAlchemyUtilsConverter


class CollisionSchema(ModelSchema):
    class Meta:
        model = Collision
        model_converter = SQLAlchemyUtilsConverter


class PositionSchema(ModelSchema):
    class Meta:
        model = Position
        model_converter = SQLAlchemyUtilsConverter


class Department1cSchema(ModelSchema):
    class Meta:
        model = Department1c
        model_converter = SQLAlchemyUtilsConverter


class RegionSchema(ModelSchema):
    class Meta:
        model = Region
        model_converter = SQLAlchemyUtilsConverter


class PollSchema(ModelSchema):
    class Meta:
        model = Poll
        model_converter = SQLAlchemyUtilsConverter


class QuestionSchema(ModelSchema):
    poll = fields.Nested(PollSchema)

    class Meta:
        model = Question
        model_converter = SQLAlchemyUtilsConverter


class VariantSchema(ModelSchema):
    question = fields.Nested(QuestionSchema)

    class Meta:
        model = Variant
        model_converter = SQLAlchemyUtilsConverter


class StatisticsSchema(ModelSchema):
    poll = fields.Nested(PollSchema)

    class Meta:
        model = Statistics
        model_converter = SQLAlchemyUtilsConverter


class PasswordSchema(ModelSchema):
    poll = fields.Nested(PollSchema)

    class Meta:
        model = Password
        model_converter = SQLAlchemyUtilsConverter


class PersonSchema(ModelSchema):
    poll = fields.Nested(PollSchema)
    birthday = fields.Date('%Y-%m-%d')
    date_of_issue = fields.Date('%Y-%m-%d')

    class Meta:
        model = Person
        model_converter = SQLAlchemyUtilsConverter


class AnswerSchema(ModelSchema):
    person = fields.Nested(PersonSchema)
    question = fields.Nested(QuestionSchema)

    class Meta:
        model = Answer
        model_converter = SQLAlchemyUtilsConverter


class LanguageSchema(ModelSchema):
    # person = fields.Nested(PersonSchema)

    class Meta:
        model = Language
        model_converter = SQLAlchemyUtilsConverter


class MilitaryServiceSchema(ModelSchema):
    # person = fields.Nested(PersonSchema)

    class Meta:
        model = MilitaryService
        model_converter = SQLAlchemyUtilsConverter


class PrioritySchema(ModelSchema):
    person = fields.Nested(PersonSchema)

    class Meta:
        model = Priority
        model_converter = SQLAlchemyUtilsConverter


class FamilySchema(ModelSchema):
    person = fields.Nested(PersonSchema)
    birthday = fields.Date('%Y-%m-%d')

    class Meta:
        model = Family
        model_converter = SQLAlchemyUtilsConverter


class DocumentSchema(ModelSchema):
    person = fields.Nested(PersonSchema)

    class Meta:
        model = Document
        model_converter = SQLAlchemyUtilsConverter


class ExperienceSchema(ModelSchema):
    person = fields.Nested(PersonSchema)

    class Meta:
        model = Experience
        model_converter = SQLAlchemyUtilsConverter


class RecommendationSchema(ModelSchema):
    person = fields.Nested(PersonSchema)

    class Meta:
        model = Recommendation
        model_converter = SQLAlchemyUtilsConverter


class EducationSchema(ModelSchema):
    person = fields.Nested(PersonSchema)

    class Meta:
        model = Education
        model_converter = SQLAlchemyUtilsConverter


class NoteSchema(ModelSchema):
    person = fields.Nested(PersonSchema)

    class Meta:
        model = Note
        model_converter = SQLAlchemyUtilsConverter


class CitySchema(ModelSchema):
    region = fields.Nested(RegionSchema)

    class Meta:
        include_fk = True
        model = City
        model_converter = SQLAlchemyUtilsConverter

class BranchSchema(ModelSchema):
    city = fields.Nested(CitySchema)

    class Meta:
        include_fk = True
        model = Branch
        model_converter = SQLAlchemyUtilsConverter


class WorkerSchema(ModelSchema):
    position = fields.Nested(PositionSchema)
    branch = fields.Nested(BranchSchema)
    person = fields.Nested(PersonSchema)
    department = fields.Nested(Department1cSchema)
    started_to_work = fields.Date('%Y-%m-%d')
    finished_to_work = fields.Date('%Y-%m-%d')

    class Meta:
        model = Worker
        model_converter = SQLAlchemyUtilsConverter


class SalarySchema(ModelSchema):
    position = fields.Nested(PositionSchema)
    worker = fields.Nested(WorkerSchema)

    class Meta:
        model = Salary
        model_converter = SQLAlchemyUtilsConverter


class VacationSchema(ModelSchema):
    worker = fields.Nested(WorkerSchema)

    class Meta:
        model = Vacation
        model_converter = SQLAlchemyUtilsConverter


class UsedVacationSchema(ModelSchema):
    vacation = fields.Nested(VacationSchema)
    start_date = fields.Date('%Y-%m-%d')
    end_date = fields.Date('%Y-%m-%d')

    class Meta:
        model = UsedVacation
        model_converter = SQLAlchemyUtilsConverter


if __name__ == '__main__':
    engine = create_engine('sqlite://')
    session = scoped_session(sessionmaker(bind=engine))
    Base.metadata.create_all(engine)

    insrt1 = Vacation(count=20, used=5)
    insrt2 = UsedVacation(count=113, year=70, vacation=insrt1)
    insrt3 = UsedVacation(count=111, year=71)
    session.add_all([insrt1, insrt2, insrt3])
    session.commit()

    result = session.query(UsedVacation).all()

    test_converter = UsedVacationSchema(many=True, exclude=['vacation.count',
                                                            'vacation.balance'])  # Виключить з результату поля vacation.count, vacation.balance, всі інші поля відображатимуть без змін
    test2_converter = UsedVacationSchema(many=True, only=['filename',
                                                          'vacation.used'])  # Включить в результат тільки поля filename, vacation.used, всі інші поля будуть виключені з результату
    dumps_data = test2_converter.dump(result).data
    pprint(dumps_data)
