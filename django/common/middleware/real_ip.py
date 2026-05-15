# common/middleware/real_ip.py
import re
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

IP_REGEX = re.compile(
    r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
    r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    r'|^([0-9a-f]{0,4}:){2,7}[0-9a-f]{0,4}$'
)

class RealIPMiddleware(MiddlewareMixin):

    def process_request(self,request):

        remote_addr=request.META.get(
            "REMOTE_ADDR"
        )

        trusted=getattr(
            settings,
            "TRUSTED_PROXIES",
            ["127.0.0.1","::1"]
        )

        if remote_addr not in trusted:
            return

        xff=request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )

        if xff:

            ip=xff.split(",")[0].strip()

            if IP_REGEX.match(ip):
                request._real_ip=ip
                request.META["REMOTE_ADDR"]=ip