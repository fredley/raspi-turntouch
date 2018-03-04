import subprocess


class BashController:

    def perform(self, action):
        try:
            print(subprocess.check_output(action['command'],
                                          shell=True
            ).decode('utf-8').strip())
        except Exception as e:
            print("Something went wrong: {}".format(e))
