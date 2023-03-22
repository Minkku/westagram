from django.test import TestCase

import json
import re   
import bcrypt
import jwt

from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from django.conf import settings    

client = Client()

REGEX_EMAIL = '^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
REGEX_PASSWORD = '^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'

class SignUpViewTest(TestCase):
    def test_signup_success(self):
        # 유효한 회원가입 정보
        valid_data = {
            "name": "test",
            "email": "test@example.com",
            "password": "Test1234!",
            "mobile": "01012345678"
        }
        response = client.post(reverse("signup"), data=json.dumps(valid_data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "SUCCESS"})
        
        # 회원가입 후 생성된 유저가 DB에 저장되었는지 확인
        user = User.objects.get(email=valid_data["email"])
        self.assertEqual(user.name, valid_data["name"])
        self.assertEqual(user.email, valid_data["email"])
        self.assertTrue(bcrypt.checkpw(valid_data["password"].encode("utf-8"), user.password.encode("utf-8")))
        self.assertEqual(user.mobile, valid_data["mobile"])

    def test_signup_invalid_email(self):
        # 이메일이 유효하지 않은 경우
        invalid_data = {
            "name": "test",
            "email": "testexample.com",    # 이메일 형식에 맞지 않음
            "password": "Test1234!",
            "mobile": "01012345678"
        }
        response = client.post(reverse("signup"), data=json.dumps(invalid_data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid email address"})

    def test_signup_invalid_password(self):
        # 비밀번호가 유효하지 않은 경우
        invalid_data = {
            "name": "test",
            "email": "test@example.com",
            "password": "test1234",    # 비밀번호 형식에 맞지 않음
            "mobile": "01012345678"
        }
        response = client.post(reverse("signup"), data=json.dumps(invalid_data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid password"})
        
    def test_signup_email_already_exists(self):
        # 이미 존재하는 이메일로 가입하는 경우
        User.objects.create(
            name="test",
            email="test@example.com",
            password=bcrypt.hashpw("Test1234!".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            mobile="01012345678"
        )
        data = {
            "name": "test",
            "email": "test@example.com",
            "password": "Test1234!",
            "mobile": "01012345678"
        }
        response = client.post(reverse("signup"), data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Email already exists"})

