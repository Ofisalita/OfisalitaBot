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

def save_acronyms():
    with open("data/acronyms.json", "w", encoding="utf8") as acronyms_data:
        json.dump(data.acronyms, acronyms_data, indent=4, ensure_ascii=False)