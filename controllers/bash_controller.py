import logging
import subprocess

from .base_controller import BaseController

class BashController(BaseController):

    def perform(self, action):
        try:
            self.log(subprocess.check_output(action['command'],
                                          shell=True
            ).decode('utf-8').strip())
        except Exception as e:
            self.log("Something went wrong: {}".format(e), logging.ERROR)
