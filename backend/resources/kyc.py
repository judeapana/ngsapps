import werkzeug
from flask import request
from flask_jwt_extended import current_user, jwt_required
from flask_restplus import Resource, fields, abort, Namespace
from flask_restplus.reqparse import RequestParser

from backend import pagination, db
from backend.common import phone_number
from backend.common.schema import KYCSchema
from backend.models import Kyc
from backend.resources.users import user_schema
from backend.utils import delete_file, file_upload

parser = RequestParser(bundle_errors=True, trim=True)

parser.add_argument('business_name', required=True, location='json', type=str)
parser.add_argument('ident', required=True, location='json', type=str)
parser.add_argument('about_business', required=True, location='json', type=str)
parser.add_argument('phone_number', required=True, location='json', type=phone_number)
parser.add_argument('country', required=True, location='json', type=str)

ns_kyc = Namespace('kyc', 'Know your customer')
schema = KYCSchema()

mschema = ns_kyc.model('KYC', {
    'user': fields.Nested(user_schema),
    'business_name': fields.String(),
    'ident': fields.String(),
    'about_business': fields.String(),
    'phone_number': fields.String(),
    'country': fields.String(),
    'file': fields.String(),
    'status': fields.String(),
})


class KYCResourceList(Resource):
    method_decorators = [jwt_required]
    """
    This is for administrators
    """

    def get(self):
        return pagination.paginate(Kyc, schema, True)


class KYCResource(Resource):
    method_decorators = [jwt_required]

    @ns_kyc.marshal_with(mschema)
    def get(self, pk):
        obj = Kyc.query.get_or_404(pk)
        return obj

    # @api.marshal_with(mschema)
    def put(self, pk):
        put_parser = RequestParser()
        put_parser.add_argument('status', required=True, location='json', type=str,
                                choices=['Approved', 'Pending', 'Disapproved', 'Suspended', 'Processing'])
        args = put_parser.parse_args(strict=True)
        kyc = Kyc.query.get_or_404(pk)
        kyc.status = args.status
        kyc.save()
        return kyc

    def delete(self, pk):
        kyc = Kyc.query.get_or_404(pk)
        return kyc.delete(), 202


##

class ClientKYCResource(Resource):
    method_decorators = [jwt_required]
    mschema.pop('user')

    @ns_kyc.marshal_with(mschema)
    def get(self):
        return current_user.kyc_doc

    def post(self):
        args = parser.parse_args(strict=True)
        if not current_user.kyc_doc:
            kyc = Kyc(**args)
            kyc.user_id = current_user.id
            return kyc.save(**args)
        return {'message': 'Resource already exist'}, 409

    def put(self):
        if current_user.kyc_doc:
            args = parser.parse_args(strict=True)
            kyc = schema.load(data=request.json, instance=current_user.kyc_doc, session=db.session, unknown='exclude')
            return kyc.save(**args), 200
        else:
            return abort(404)

    def delete(self):
        doc = current_user.kyc_doc
        if doc:
            delete_file(doc.file)
            return doc.delete(), 202
        return abort(404)


class KycUploadResource(Resource):
    method_decorators = [jwt_required]
    file_parser = RequestParser(bundle_errors=True)

    @ns_kyc.marshal_with(mschema)
    def post(self):
        # if current_user.kyc_doc.status == 'Approved':
        #     return {'message': 'You documents are approval'}
        KycUploadResource.file_parser.add_argument('file', required=True, location='files',
                                                   type=werkzeug.datastructures.FileStorage)
        args = KycUploadResource.file_parser.parse_args(strict=True)
        kyc = current_user.kyc_doc
        if kyc.file:
            delete_file(kyc.file)
        file = file_upload(args.file)
        file.get('upload').save(file.get('full_path'))
        kyc.file = file.get('filename')
        kyc.save()
        return kyc, 200


ns_kyc.add_resource(KYCResourceList, '/', endpoint='kycs')
ns_kyc.add_resource(KYCResource, '/<int:pk>', endpoint='kyc')
ns_kyc.add_resource(ClientKYCResource, '/client', endpoint='client_kyc')
ns_kyc.add_resource(KycUploadResource, '/client/file', endpoint='client_kyc_file')
