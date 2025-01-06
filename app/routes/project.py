from flask import request, jsonify, make_response, current_app, url_for
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from ..models.project import Project
from http import HTTPStatus
import traceback
import os
from werkzeug.utils import secure_filename
import time

api = Namespace('projects', description='Quản lý dự án')

project_model = api.model('Project', {
    'title': fields.String(required=True),
    'description': fields.String(required=True),
    'category': fields.String(required=True),
    'image': fields.String(required=True),
    'progress': fields.Integer(required=True),
    'teamSize': fields.Integer(required=True),
    'technologies': fields.List(fields.String, required=True),
    'links': fields.Raw(required=True),
    'details': fields.String(required=False),
    'teamMembers': fields.List(fields.Raw, required=False)
})

@api.route('/')
class ProjectList(Resource):
    @api.doc('list_projects')
    def get(self):
        """Lấy danh sách tất cả dự án"""
        try:
            projects = Project.get_all()
            return {
                'message': 'Lấy danh sách dự án thành công',
                'data': [project.__dict__ for project in projects]
            }, HTTPStatus.OK
        except Exception as e:
            print(f"Error getting projects: {str(e)}")
            print(traceback.format_exc())
            return {
                'message': 'Lỗi khi lấy danh sách dự án',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR

    @api.doc('create_project')
    @api.expect(project_model)
    @jwt_required()
    def post(self):
        """Tạo dự án mới"""
        try:
            data = request.get_json()
            new_project = Project.create(data)
            return {
                'message': 'Tạo dự án mới thành công',
                'data': new_project.__dict__
            }, HTTPStatus.CREATED
        except Exception as e:
            print(f"Error creating project: {str(e)}")
            print(traceback.format_exc())
            return {
                'message': 'Lỗi khi tạo dự án mới',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR

@api.route('/<int:id>')
class ProjectResource(Resource):
    @api.doc('get_project')
    def get(self, id):
        """Lấy thông tin một dự án"""
        try:
            project = Project.get_by_id(id)
            if project:
                return {
                    'message': 'Lấy thông tin dự án thành công',
                    'data': project.__dict__
                }, HTTPStatus.OK
            return {
                'message': 'Không tìm thấy dự án',
                'error': 'NOT_FOUND'
            }, HTTPStatus.NOT_FOUND
        except Exception as e:
            return {
                'message': 'Lỗi khi lấy thông tin dự án',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR

    @api.doc('update_project')
    @api.expect(project_model)
    @jwt_required()
    def put(self, id):
        """Cập nhật thông tin dự án"""
        try:
            data = request.get_json()
            updated_project = Project.update(id, data)
            if updated_project:
                return {
                    'message': 'Cập nhật dự án thành công',
                    'data': updated_project.__dict__
                }, HTTPStatus.OK
            return {
                'message': 'Không tìm thấy dự án',
                'error': 'NOT_FOUND'
            }, HTTPStatus.NOT_FOUND
        except Exception as e:
            return {
                'message': 'Lỗi khi cập nhật dự án',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR

    @api.doc('delete_project')
    @jwt_required()
    def delete(self, id):
        """Xóa dự án"""
        try:
            if Project.delete(id):
                return {
                    'message': 'Xóa dự án thành công'
                }, HTTPStatus.OK
            return {
                'message': 'Không tìm thấy dự án',
                'error': 'NOT_FOUND'
            }, HTTPStatus.NOT_FOUND
        except Exception as e:
            return {
                'message': 'Lỗi khi xóa dự án',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR 