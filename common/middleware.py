import json
import traceback
from django.http import JsonResponse
from common.exceptions import TalentIQBaseException

class GlobalErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        return self.get_response(request)
    
    def process_exception(self, request, exception):
        # Only handle our custom exceptions
        if isinstance(exception, TalentIQBaseException):
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'error': type(exception).__name__,
                    'message': str(exception)
                }, status=400)
        return None   # Let Django handle other exceptions normally
