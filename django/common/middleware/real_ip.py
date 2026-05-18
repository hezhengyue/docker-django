# common/middleware/real_ip.py
from ipware import get_client_ip
from django.utils.deprecation import MiddlewareMixin


class RealIPMiddleware(MiddlewareMixin):

    def process_request(self, request):

        ip, is_routable = get_client_ip(request)

        if ip:
            request._real_ip = ip
            request.META['REMOTE_ADDR'] = ip


def get_client_real_ip(request):

    return getattr(
        request,
        '_real_ip',
        request.META.get('REMOTE_ADDR', '0.0.0.0')
    )