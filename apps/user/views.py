from django.contrib.auth.models import AnonymousUser
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from django.http import JsonResponse
from .models import User

@api_view(['GET'])
def get_all_users(request):
    """
    GET 请求接口，返回 User 集合中所有文档的数据
    """
    if request.method == 'GET':
        try:
            # 查询所有文档
            cursor = User.collection.find({})
            users = []
            for user in cursor:
                # 如果 _id 是 ObjectId 类型，则转换为字符串（如果需要）
                if '_id' in user:
                    user['_id'] = str(user['_id'])
                users.append(user)
            return JsonResponse({"data": users}, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


