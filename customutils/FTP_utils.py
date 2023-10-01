import os
import time
from ftplib import FTP

import datetime
from PIL import Image

from customutils.request_handlers import get_file_name_type


class FtpUpload:
    def __init__(self):
        self.HOSTNAME = os.getenv("FTP_SERVER")
        self.USERNAME = os.getenv("FTP_USERNAME")
        self.PASSWORD = os.getenv("FTP_PASSWORD")
        self.PORT = os.getenv("FTP_PORT")
        # self.# FTP Server Connection
        self.ftp = FTP(self.HOSTNAME, self.USERNAME, self.PASSWORD, self.PORT)

    @classmethod
    def connect_ftp(self):
        ftp_ = None
        ftp_connection_exception = False
        try:
            ftp_ = FtpUpload()
        except Exception as e:
            self.ftp_ = str(e)
            ftp_connection_exception = True
        finally:
            return ftp_, ftp_connection_exception

    def connect(self):
        try:
            self.ftp.connect(self.HOSTNAME, int(self.PORT))
            if self.login():
                return True
            else:
                return False
        except Exception as e:
            print(" exception  ", e)
            return False

    def login(self):
        try:
            self.ftp.login(self.USERNAME, self.PASSWORD)
            return True
        except Exception as e:
            print(e)
            return False

    def directory_exists(self, dir):
        filelist = []
        self.ftp.retrlines("LIST", filelist.append)
        for f in filelist:
            if f.split()[-1] == dir and f.upper().startswith("D"):
                return True
        return False

    def chdir(self, dir):
        if self.directory_exists(dir) is False:
            self.ftp.mkd(dir)
        self.ftp.cwd(dir)

    def create_directory_name(self):
        dir_name = str(datetime.datetime.now().timestamp())
        a, b, c = dir_name.partition(".")
        dir_name = a + c
        return int(dir_name)

    def quit_server(self):
        self.ftp.quit()

    def store_tiff_image(self, file, extension_num):
        outfile = file.name[:-extension_num] + "jpeg"
        im = Image.open(file)
        out = im.convert("RGB")
        out.save(outfile, "JPEG", quality=90)
        self.ftp.storbinary("STOR " + f"{outfile}", open(outfile, "rb"))

    def convert_tiff_to_jpeg(self, file, file_extension):
        if file_extension in [".tiff", ".tif"] or file.name[-3:] == "bmp":
            if file_extension == ".tif":
                self.store_tiff_image(file=file, extension_num=3)
            elif file_extension == ".tiff":
                self.store_tiff_image(file=file, extension_num=4)
            else:
                self.store_tiff_image(file=file, extension_num=3)

    def add_target_image(self, file, directory_name, file_extension):
        """
        Store file on ftp server
        :param file_extension:
        :param file:
        :param directory_name:
        :return:
        """
        if self.is_connected():
            print("1 In add target image =================================")
            self.chdir(f"{os.getenv('BASE_PATH')}{directory_name}")
            print("2 In image directory ==================================")
            # for file in list(files):  # In case of multiple images in single unique directory

            self.ftp.storbinary("STOR " + f"{file.name}", file.file)
            if file_extension in [".tif", ".tiff"]:
                self.convert_tiff_to_jpeg(file_extension=file_extension, file=file)

            ftp_image_path = f"{os.getenv('BASE_PATH')}{str(directory_name)}"
            return ftp_image_path
        else:
            print("connection failed")
            return False

    def is_connected(self):
        try:
            return True
        except:
            return False

    def create_image_link(self, directory, file_name):
        try:
            self.ftp.cwd(dirname=directory)
            directory = directory.replace(
                os.getenv("REPLACE_FTP_PATH"), ""
            )  # to create a successful image link
            links = [
                f"http://{os.getenv('FTP_SERVER')}{directory}/{i}"
                for i in self.ftp.nlst()
            ]
            if file_name[-3:] == "tif" or file_name[-4:] == "tiff":
                return links[1]
            else:
                return links[0]
        except Exception as e:
            print(e)

    def retry_ftp_connection(self):
        is_connected = False
        for i in range(5):  # 5 retries
            if self.connect():
                if self.login():
                    is_connected = True
                    return is_connected
            else:
                error = "FTP Connection Error"
                E = self.ftp.connect()

        return is_connected
