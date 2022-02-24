from os import path

from telegram.ext import PicklePersistence

persistence = PicklePersistence(path.relpath('db'))
