import logging
import subprocess

logger = logging.getLogger('bash_controller')


class BashController:

    def perform(self, action):
        try:
            logger.log(subprocess.check_output(action['command'],
                                          shell=True
            ).decode('utf-8').strip())
        except Exception as e:
            logger.log("Something went wrong: {}".format(e))
