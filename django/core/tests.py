# core/tests.py
from django.test import TestCase
from common.email.password import send_temp_password_email, generate_secure_password

class EmailTest(TestCase):
    def test_send_password_email(self):
        pwd = generate_secure_password()
        result = send_temp_password_email(
            user_email="hezhengyue@aliyun.com",
            password=pwd,
            username="测试用户"
        )
        self.assertTrue(result)