import logging
from app import app

from candidate import candidate
from collision import collision
from document import document
from education import education
from experience import experience
from family import family
from note import note
from other import other
from person import person
from places import places
from poll import poll
from vacation import vacation
from worker import worker

if __name__ == '__main__':
    handler = logging.FileHandler('history.log', encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    app.register_blueprint(candidate)
    app.register_blueprint(collision)
    app.register_blueprint(document)
    app.register_blueprint(education)
    app.register_blueprint(experience)
    app.register_blueprint(family)
    app.register_blueprint(note)
    app.register_blueprint(other)
    app.register_blueprint(person)
    app.register_blueprint(places)
    app.register_blueprint(poll)
    app.register_blueprint(vacation)
    app.register_blueprint(worker)

    app.run(port=5666, debug=True, threaded=True)
    # app.run(host='0.0.0.0', port=5555, threaded=True)
