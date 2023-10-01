import os

import filetype

from apps.data_source.enums.type import DataTypeChoices
from apps.data_source.models import AIServices
from apps.users.models import UserRoles


class RequestHandler:
    @classmethod
    def get_user_id(cls, request):
        user_id = None
        try:
            user_id = request.user.id
        except:
            user_id = None
        finally:
            return user_id

    @classmethod
    def get_user(cls, request):
        user = None
        try:
            user = request.user
        except:
            user = None
        finally:
            return user

    @classmethod
    def get_user_role(cls, request):
        role = None
        try:
            role_key = cls.get_request_data(request=request, key="role_key")
            role = UserRoles.get_role(role_key=role_key)
        except:
            role = None
        finally:
            return role

    @classmethod
    def get_files(cls, request):
        file_list = None
        try:
            file_list = request.FILES.getlist("file")
        except:
            file_list = None
        finally:
            return file_list



    @classmethod
    def get_request_data(cls, request, key):
        file_type = None
        try:
            file_type = request.data.get(key)
        except:
            file_type = None
        finally:
            return file_type

    @classmethod
    def get_service_type(cls, request):
        service = None
        try:
            service_type_key = cls.get_request_data(request=request, key="service_type")
            service_obj = AIServices.get_service(service_key=service_type_key)
            if service_obj:
                service = service_obj.pk

        except:
            service = None
        finally:
            return service


def get_file_name_type(file):
    filename = None
    file_type = None
    try:
        filename, file_extension = os.path.splitext(file.name)

        kind = filetype.guess(file).mime.split("/")[0]
        if kind == "image":
            if file_extension in [".tiff", ".tif"]:
                file_type = DataTypeChoices.SATELLITE
            else:
                file_type = DataTypeChoices.IMAGE
        elif kind == "video":
            file_type = DataTypeChoices.VIDEO
        elif kind == "audio":
            file_type = DataTypeChoices.AUDIO
        else:
            file_type = None
    except:
        filename = None
        file_type = None
    finally:
        if file_type is None:
            raise Exception
        else:
            return filename, file_type
