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

    @classmethod
    def help(cls):
      return """
Bash Module - Run commands in the shell

Usage:

north_press:
  type: bash
  command: echo "Hello North"
"""

