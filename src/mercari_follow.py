#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import logging.handlers

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

import os
import sys
import random
import time
import pathlib
import traceback

from selenium_util import (
    create_driver,
    click_xpath,
    dump_page,
    clean_dump,
    random_sleep,
    log_memory_usage,
)
import logger
import mercari
from config import load_config
import notify_slack

SLEEP_UNIT = 60
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


def sleep_until(end_time):
    sleep_remain = end_time - time.time()
    logging.info("sleep {sleep:,} sec...".format(sleep=int(sleep_remain)))

    while True:
        # NOTE: Livenss がタイムアウトしないよう，定期的に更新する
        pathlib.Path(config["liveness"]["file"]).touch()

        sleep_remain = end_time - time.time()
        if sleep_remain < 0:
            return
        elif sleep_remain < SLEEP_UNIT:
            time.sleep(sleep_remain)
        else:
            time.sleep(SLEEP_UNIT)


def item_follow(driver, wait, profile, item):
    logging.info("{id} を処理します．".format(id=item["id"]))
    driver.get(ITEM_URL.format(id=item["id"]))

    wait.until(EC.presence_of_element_located((By.XPATH, "//textarea")))
    status_text = driver.find_element(By.XPATH, '//p[@slot="title"]').text

    if status_text != "商品の発送を通知しました":
        logging.warning(
            "ステータスが想定と異なるので，スキップします．(status: {status}".format(status=status_text)
        )
        return

    driver.find_element(By.XPATH, '//textarea[@name="chat"]').send_keys(item["comment"])
    click_xpath(driver, '//button[contains(text(), "取引メッセージを送る")]', wait)
    wait.until(EC.presence_of_element_located((By.XPATH, "//textarea")))

    logging.info("完了しました．")


def do_follow_items(driver, wait, item_list):
    for item in item_list:
        item_follow(driver, wait, profile, item)
        random_sleep(3)


def do_work(config, profile):
    driver = create_driver(profile["name"])

    wait = WebDriverWait(driver, WAIT_TIMEOUT_SEC)
    ret_code = -1

    try:
        mercari.warmup(driver)

        mercari.login(config, driver, wait, profile)

        do_follow_items(driver, wait, profile["target"])

        log_memory_usage(driver)

        logging.info("Finish.")
        ret_code = 0
    except:
        logging.error("URL: {url}".format(url=driver.current_url))
        logging.error(traceback.format_exc())

        if "slack" in config:
            notify_slack.error(
                config["slack"]["bot_token"],
                config["slack"]["info"]["channel"],
                traceback.format_exc(),
                config["slack"]["error"]["interval_min"],
            )

        dump_page(driver, int(random.random() * 100))
        clean_dump()

    driver.close()
    driver.quit()

    return ret_code


os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

logger.init("bot.mercari.follow")

logging.info("Start.")

while True:
    start_time = time.time()
    config = load_config()

    for profile in config["profile"]:
        do_work(config, profile)

    sleep_until(start_time + config["interval"])
