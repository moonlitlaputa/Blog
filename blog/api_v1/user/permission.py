from sanic_restful import Resource

from blog.decorators import login_requred


class PermissionAuth(Resource):

    method_decorators = [login_requred]

    async def get(self, request):
        user = request['current_user']
        if not user.is_anonymous:
            return {'permission': user.role.permissions}
        return {'permission': 0}