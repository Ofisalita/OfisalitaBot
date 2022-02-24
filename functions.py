import json

import data

from config.logger import logger

def load_acronyms():
    try:
        with open("data/acronyms.json", "r", encoding="utf8") as datajsonfile:
            data.acronyms = json.load(datajsonfile)
        logger.info("Acronyms data loaded.")
    except OSError:
        logger.error("Acronyms data not found.")