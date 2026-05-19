# jobs/handlers/mail.py

import time

from django.core.mail import send_mail

from jobs.handlers.base import BaseHandler


class MailHandler(BaseHandler):

    def handle(self):

        self.log('开始发送邮件')

        total = 10000

        for i in range(total):

            time.sleep(1)

            self.progress(i + 1, total)

            self.log(f'正在处理第 {i + 1} 封邮件')

        # 模拟发送
        send_mail(
            subject='测试邮件',
            message='这是一个测试任务邮件',
            from_email='admin@test.com',
            recipient_list=[
                'test@test.com'
            ],
            fail_silently=False,
        )

        self.log('邮件发送完成')

        return {
            'message': '邮件发送成功'
        }