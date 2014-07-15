__author__ = 'Pranay Anchuri'
import logging


def get_logger(name=None):
    if not name:
        name = "__main__"
    formatter = logging.Formatter('%(levelname)s: %(funcName)s(%(lineno)d) -- %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(name)
    fh = logging.FileHandler('%s.log' % name, mode='w')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)
    return logger
