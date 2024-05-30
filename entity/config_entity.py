import os,sys
from dataclasses import dataclass
from exception import QbitException

"""
this class is created to create entity for the video path, saving it in archive and getting the outcome 

"""
class VideoPredictionConfig:
    def __init__(self):
        try:
            self.inbox_dir = os.path.join("data","inbox")
            self.outbox_dir = os.path.join("data","outbox")
            self.archive_dir = os.path.join("data","archive")
            os.makedirs(self.outbox_dir ,exist_ok=True)
            os.makedirs(self.archive_dir,exist_ok=True)
        except Exception as e:
            raise QbitException(e, sys)