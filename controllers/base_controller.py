import logging


class BaseController:

  print_log = False

  def __init__(self, *args, **kwargs):
    if kwargs.get('print'):
      self.print_log = True
    else:
      self.logger = logging.getLogger(self.get_class_name())
    self.init(*args, **kwargs)

  @classmethod
  def get_class_name(cls):
    return cls.__name__

  def init(self):
    self.log("Initialised {}".format(self.get_class_name()))

  def log(self, msg, level=logging.INFO):
    if self.print_log:
      print(msg)
    else:
      self.logger.log(level, msg)

  def perform(self, action):
    print("Unimplemented!")

  @classmethod
  def help(cls):
    return "There is no help for this module :-("

  def print_all(self):
    pass
