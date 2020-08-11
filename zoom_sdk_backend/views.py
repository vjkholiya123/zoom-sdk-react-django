import jwt
import base64
import hashlib
import hmac
import requests
import json
import time
from django.conf import settings
from django.http import JsonResponse


def ZoomJWTToken(request):
    token = jwt.encode(
        # Create a payload of the token containing API Key & exp time
        {"iss": settings.ZOOM_API_KEY, "exp": time.time() + 60000},
        # Secret used to generate token signature
        settings.ZOOM_API_SECRET,
        # Specify the hashing alg
        algorithm='HS256'
    ).decode('utf-8')

    meeting_data = {
        "topic": "Sample Discussion",
        "type": "1",
        "duration": "60",
        "password": "IamThe",
        "agenda": "To discuss various plans meeting",
        "settings": {
            "host_video": "true",
            "participant_video": "true",
            "join_before_host": "true",
            "mute_upon_entry": "true",
            "watermark": "true",
            "use_pmi": "false",
            "approval_type": "0",
            "audio": "both",
            "auto_recording": "cloud"
        }
    }
    # simplejson(meeting_data)
    meeting_json_data = json.dumps(meeting_data)
    URL = 'https://api.zoom.us/v2/users/' + settings.ZOOM_USER_ID + '/meetings'
    print(f"URL: {URL}    Data: {meeting_json_data} \n\n Typeof dta: {type(meeting_json_data)}")
    req = requests.post(URL, data=meeting_json_data,
                        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}).json()
    return JsonResponse({'zoom_signature': token, 'meeting_response': req})


def ZoomMeetingSignature(request):
    zoom_meeting_role = '1'
    timestamp = int(round(time.time() * 1000)) - 30000
    string_message = settings.ZOOM_API_KEY + str(request.GET.get('meeting_number')) + str(timestamp) + \
                     zoom_meeting_role
    message = base64.b64encode(bytes(string_message, 'utf-8'))
    secret = bytes(settings.ZOOM_API_SECRET, 'utf-8')
    hashing = hmac.new(secret, message, hashlib.sha256)
    hashing = base64.b64encode(hashing.digest())
    hashing = hashing.decode("utf-8")
    temp_string = "%s.%s.%s.%s.%s" % (settings.ZOOM_API_KEY, str(request.GET.get('meeting_number')), str(timestamp),
                                      zoom_meeting_role, hashing)
    signature = base64.b64encode(bytes(temp_string, "utf-8"))
    signature = signature.decode("utf-8")
    print(f"Meeting No: {request.GET.get('meeting_number')}")
    return JsonResponse({'signature': signature.rstrip("=")})
