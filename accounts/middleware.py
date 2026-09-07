"""UC-02 substitute: explicit session flag instead of IP-range detection."""


class VubNetworkModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.vub_network_mode = bool(request.session.get("vub_network_mode", False))
        return self.get_response(request)
