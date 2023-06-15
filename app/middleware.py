import logging


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('app')  # 替换为实际的日志器名称

    def __call__(self, request):
        self.logger.info(f'[{request.method}] {request.path} {request.META["SERVER_PROTOCOL"]}')
        response = self.get_response(request)
        return response
