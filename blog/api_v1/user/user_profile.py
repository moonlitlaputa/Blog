from flask import g, request
from flask_restful import Resource

from blog.models import User, Permission
from blog.api_v1 import token_auth
from blog.utils.web import HTTPStatusCodeMixin


class UserProfile(Resource, HTTPStatusCodeMixin):

    decorators = [token_auth.login_required]

    def get(self):
        # 权限分离
        user = User.get(request.args.get('uid'))
        edit_permission = False
        if g.current_user == user or g.current_user.can(Permission.ADMINISTER):
            edit_permission = True

        return {
            "user": user.to_json(),
            "edit_permission": edit_permission
        }, self.SUCCESS