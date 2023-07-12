import json
import re   # 정규표현식을 사용하기 위해 씀
import bcrypt
import jwt

from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from users.models import User
from django.conf import settings    # 이렇게 호출하는 이유는 settings.py 가 분리 될 수도 있고 위치가 바뀔 수도 있기때문에.

REGEX_EMAIL    = '^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
REGEX_PASSWORD = '^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'

class SignUpView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            name = data['name']
            email = data['email']
            password = data['password']
            mobile = data['mobile']

            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            decoded_password = hashed_password.decode("utf-8")

            # 설정한 정규표현식과 맞지 않으면 오류
            # 정규표현식을 사용하기 때문에 match() 매소드 앞에 re를 붙여준다.
            # https://engineer-mole.tistory.com/189  /더 많은 re. 메소드
            if not re.match(REGEX_EMAIL, email):
                return JsonResponse({'error': 'Invalid email address'}, status=400)
            
            if not re.match(REGEX_PASSWORD, password):
                return JsonResponse({'error': 'Invalid password'}, status=400)
            
            # DB안에 같은 이메일 정보가 있으면 오류
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)

            User.objects.create(
                name = name,
                email = email,
                password = decoded_password,
                mobile = mobile
            )

            return JsonResponse({"message": "SUCCESS"}, status=200)
        
        except KeyError:
            return JsonResponse({'error': 'KEY ERROR'}, status=400)
        
class SignInView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            email = data['email']
            password = data['password']

            if not bcrypt.checkpw(password.encode("utf-8"), User.objects.get(email=email).password.encode("utf-8")):
                return JsonResponse({'error': 'INVALID USER OR PASSWORD'}, status=400)
            
            encoded_jwt = jwt.encode({'id': User.objects.get(email=email).id}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
            return JsonResponse({'token': encoded_jwt}, status=200)

        except KeyError:
            return JsonResponse({'error': 'KEY ERROR'}, status=400)
        
        except User.DoesNotExist:
            return JsonResponse({"error": "DOESNOTEXIST ERROR" }, status=400)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Json Error"}, status=400)