#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import logging.handlers
import os
import pathlib
import random
import traceback

import mercari
import notify_slack
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium_util import clean_dump, click_xpath, create_driver, dump_page, log_memory_usage, random_sleep

WAIT_TIMEOUT_SEC = 15

DATA_PATH = pathlib.Path(os.path.dirname(__file__)).parent / "data"
LOG_PATH = DATA_PATH / "log"

CHROME_DATA_PATH = DATA_PATH / "chrome"
RECORD_PATH = str(DATA_PATH / "record")
DUMP_PATH = str(DATA_PATH / "debug")

DRIVER_LOG_PATH = str(LOG_PATH / "webdriver.log")
HIST_CSV_PATH = str(LOG_PATH / "history.csv")

ITEM_URL = "https://jp.mercari.com/transaction/{id}"


def execute_item(driver, wait, profile, item):
    logging.info("{id} を処理します．".format(id=item["id"]))
    driver.get(ITEM_URL.format(id=item["id"]))

    wait.until(EC.presence_of_element_located((By.XPATH, "//textarea")))
    status_text = driver.find_element(By.XPATH, '//aside[@data-partner-id="status-banner"]').get_attribute(
        "aria-label"
    )

    if status_text != item["status"]:
        logging.warning("ステータスが想定と異なるので，スキップします．(status: {status}".format(status=status_text))
        return

    driver.find_element(By.XPATH, '//textarea[@name="chat"]').send_keys(item["comment"])
    click_xpath(driver, '//button[contains(text(), "取引メッセージを送る")]', wait)
    wait.until(EC.presence_of_element_located((By.XPATH, "//textarea")))

    logging.info("完了しました．")


def iterate_target(driver, wait, profile):
    for item in profile["target"]:
        execute_item(driver, wait, profile, item)
        random_sleep(3)


def execute(config, profile, mode):
    driver = create_driver(profile["name"])

    wait = WebDriverWait(driver, WAIT_TIMEOUT_SEC)
    ret_code = -1

    try:
        mercari.warmup(driver)

        mercari.login(config, driver, wait, profile)

        iterate_target(driver, wait, profile)

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
