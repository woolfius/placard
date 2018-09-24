import base64
import io

from flask import Blueprint, send_file, jsonify
from flask_login import login_required

from alchemybase import Document
from db import Session
from marshmallow_schemas import DocumentSchema

document = Blueprint('document', __name__)


@document.route('/get/document/<_id>', methods=['POST', 'GET'])
@login_required
def get_document_id(_id):
    """
    Повертає документ. В групу Document
    :param _id: ід документа
    """
    session = Session()
    response = session.query(Document.file, Document.file_type).filter_by(id=_id).first()
    session.close()
    if response == None:
        return 'False'
    gif_str = base64.b64decode(response[0])
    return send_file(io.BytesIO(gif_str), mimetype=response[1])


@document.route('/documents/<_id>', methods=['GET'])
@login_required
def worker_documents(_id):
    """
    Повертає список документів фіз особи. В групу Document
    :param id_: фіз особи
    """
    session = Session()
    all_records = session.query(Document).filter_by(fk_person=_id).all()
    converter = DocumentSchema(many=True, only=['id', 'name', 'file_type', 'created', 'status', 'type_', 'fk_person'])
    response = converter.dump(all_records).data
    session.close()
    return jsonify(response)


@document.route('/api/documents/change/<_id>/<status>', methods=['POST'])
@login_required
def foto_documents_cgange(_id, status):
    """
    Змінює статус документу active/not active для відображення документів. В групу Documents
    :param _id: ід документу
    :param status: active/not active
    """
    session = Session()
    session.query(Document).filter_by(id=_id).update({"status": status})
    session.commit()
    session.close()
    return 'ok'
