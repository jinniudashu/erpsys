from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
import json

def serialize_request(request: HttpRequest) -> str:
    request_dict = {
        'path': request.path,
        'method': request.method,
        'GET': request.GET.dict(),
        'POST': request.POST.dict(),
        'COOKIES': request.COOKIES,
        'META': {key: value for key, value in request.META.items() if isinstance(value, (str, int, bool))},
        'user': request.user.username if request.user.is_authenticated else None,
    }
    return json.dumps(request_dict)

def deserialize_request(request_json: str) -> HttpRequest:
    request_dict = json.loads(request_json)
    
    request = HttpRequest()
    request.path = request_dict.get('path', '')
    request.method = request_dict.get('method', 'GET')
    
    request.GET = request_dict.get('GET', {})
    request.POST = request_dict.get('POST', {})
    request.COOKIES = request_dict.get('COOKIES', {})
    
    # Only include META keys that are safe and necessary for your use case
    request.META.update(request_dict.get('META', {}))
    
    user = request_dict.get('user')
    if user:
        try:
            request.user = User.objects.get(username=user)
        except User.DoesNotExist:
            request.user = AnonymousUser()
    else:
        request.user = AnonymousUser()
    
    return request
