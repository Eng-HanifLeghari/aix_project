import ast
import json
from rest_framework import permissions, status


class ResponseFormatMiddleware:
    """
    Custom middleware for changing response
    """
    admin_panel_check = None
    rendered_content = None

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.admin_panel_check = None
        response = self.get_response(request)
        my_respnse = ast.literal_eval(str(response.content))
        try:
            self.rendered_content = response.rendered_content
        except:
            self.rendered_content = None
        try:
            self.admin_panel_check = response.accepted_renderer
        except:
            self.admin_panel_check = None
        if self.admin_panel_check is not None:
            my_data = json.loads(my_respnse)

            if my_data.get("code", "") == 'token_not_valid':
                try:
                    json_response = {"statusMessage":"Token not valid or expired","data" : [] , "statusCode":status.HTTP_401_UNAUTHORIZED, "errorStatus": "True"}
                    json_to_sring = json.dumps(json_response)
                    string_to_bytes = json_to_sring.encode()
                    response.content = string_to_bytes
                    response.status_code = 200
                except AttributeError:
                    pass
            if my_data.get("access", None) and my_data.get("refresh", None):
                access_Token = my_data.get("access", None)
                refresh_Token = my_data.get("refresh", None)
                json_response = {"statusMessage":"Token refreshed successfully","data" : {"access_token" : access_Token , "refresh_token" : refresh_Token} , "statusCode":status.HTTP_200_OK, "errorStatus": "False"}
                json_to_sring = json.dumps(json_response)
                string_to_bytes = json_to_sring.encode()
                response.content = string_to_bytes
                response.status_code = 200

        return response
