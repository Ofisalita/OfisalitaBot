from telegram.ext import Updater

from config.auth import token
from config.persistence import persistence

updater = Updater(token=token, use_context=True, persistence=persistence)
dp = updater.dispatcher
jq = updater.job_queue
