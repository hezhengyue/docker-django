def get_client_ip(request):

    return getattr(
        request,
        "_real_ip",
        request.META.get(
            "REMOTE_ADDR",
            "0.0.0.0"
        )
    )