#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import bz2
import io
import logging
import logging.handlers
import os

import coloredlogs

LOG_FORMAT = "{name} %(asctime)s %(levelname)s [%(filename)s:%(lineno)s %(funcName)s] %(message)s"


class GZipRotator:
    def namer(name):
        return name + ".bz2"

    def rotator(source, dest):
        with open(source, "rb") as fs:
            with bz2.open(dest, "wb") as fd:
                fd.writelines(fs)
        os.remove(source)


def init(name, level=logging.WARNING, is_str=False):
    coloredlogs.install(fmt=LOG_FORMAT.format(name=name), level=level)

    if is_str:
        str_io = io.StringIO()
        handler = logging.StreamHandler(str_io)
        handler.formatter = logging.Formatter(fmt=LOG_FORMAT.format(name=name), datefmt="%Y-%m-%d %H:%M:%S")
        logging.getLogger().addHandler(handler)

        return str_io


if __name__ == "__main__":
    init("test")
    logging.info("Test")
