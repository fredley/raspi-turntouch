import logging


class BaseController:

  print_log = False

  def __init__(self, *args, **kwargs):
    if kwargs.get('print'):
      self.print_log = True
    else:
      self.logger = logging.getLogger(type(self).__name__)
    self.init()

  def init(self):
    print("Initialised {}".format(type(self).__name__))

  def log(self, msg, level=logging.INFO):
    if self.print_log:
      print(msg)
    else:
      self.logger.log(level, msg)

  def perform(self, action):
    print ("Unimplemented!")
