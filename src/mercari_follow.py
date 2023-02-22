#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import logging.handlers

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support import expected_conditions as EC

import time
import os
import sys
import random
import re

import pathlib
import traceback

from selenium_util import (
    create_driver,
    click_xpath,
    wait_patiently,
    dump_page,
    clean_dump,
    random_sleep,
    log_memory_usage,
)
import logger
import mercari
from config import load_config

WAIT_TIMEOUT_SEC = 15

DATA_PATH = pathlib.Path(os.path.dirname(__file__)).parent / "data"
LOG_PATH = DATA_PATH / "log"

CHROME_DATA_PATH = DATA_PATH / "chrome"
RECORD_PATH = str(DATA_PATH / "record")
DUMP_PATH = str(DATA_PATH / "debug")

DRIVER_LOG_PATH = str(LOG_PATH / "webdriver.log")
HIST_CSV_PATH = str(LOG_PATH / "history.csv")

ITEM_URL = "https://jp.mercari.com/transaction/{id}"

# NOTE: True にすると，最初のアイテムだけ処理され，価格変更も行われない
DEBUG = False


def item_price_down(driver, wait, profile, item):
    logging.info("{id} を処理します．".format(id=item["id"]))
    driver.get(ITEM_URL.format(id=item["id"]))

    wait.until(EC.presence_of_element_located((By.XPATH, "//textarea")))
    status_text = driver.find_element(By.XPATH, '//mer-text[@slot="title"]').text

    if status_text != "商品の発送を通知しました":
        logging.warning(
            "ステータスが想定とこなるので，スキップします．(status: {status}".format(status=status_text)
        )
        return

    driver.find_element(By.XPATH, '//textarea[@name="chat"]').send_keys(item["comment"])
    click_xpath(driver, '//button[contains(text(), "取引メッセージを送る")]', wait)
    wait.until(EC.presence_of_element_located((By.XPATH, "//textarea")))

    logging.info("完了しました．")


def follow_items(driver, wait, item_list):
    for item in item_list:
        item_price_down(driver, wait, profile, item)


def do_work(config, profile):
    driver = create_driver(profile["name"])

    wait = WebDriverWait(driver, WAIT_TIMEOUT_SEC)
    ret_code = -1

    try:
        mercari.warmup(driver)

        mercari.login(config, driver, wait, profile)

        follow_items(driver, wait, profile["target"])

        log_memory_usage(driver)

        logging.info("Finish.")
        ret_code = 0
    except:
        logging.error("URL: {url}".format(url=driver.current_url))
        logging.error(traceback.format_exc())
        dump_page(driver, int(random.random() * 100))
        clean_dump()

    driver.close()
    driver.quit()

    return ret_code


os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

logger.init("bot.mercari.inventory")

logging.info("Start.")

config = load_config()

ret_code = 0
for profile in config["profile"]:
    ret_code += do_work(config, profile)

sys.exit(ret_code)