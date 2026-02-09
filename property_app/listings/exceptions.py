from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

# Global error and response handler
def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # return None if DRF cant handle it. Django will raise a 500
    if response is None:
        return None
    
    return Response(
        {
            "success": False,
            "status_code": response.status_code,
            "error": response.data,
        },
        status = response.status_code,
        headers = response.headers,
    )