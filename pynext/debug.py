"""
The MIT License (MIT)
Copyright (c) 2023-present xXenvy

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

import logging
from colorlog import ColoredFormatter
from typing import Literal


class DebugLogger:
    """
    DebugLogger used to log library logs.

    Parameters
    ----------
    logger:
        Debug logger object.

    Attributes
    ----------
    logger:
        Debug logger object.
    """
    __slots__ = ('logger',)

    def __init__(self, logger: logging.Logger) -> None:
        self.logger: logging.Logger = logger

    @classmethod
    def run(
            cls,
            module: Literal['pynext', 'pynext.rest', 'pynext.gateway', 'pynext.common'] = 'pynext',
            colored: bool = True,
            level: int = logging.DEBUG,
            file_path: str | None = None) -> DebugLogger:
        """
        Classmethod Which creates a logger class.

        Parameters
        ----------
        module:
            Module that the logger is supposed to listen to. The library has 3 logger modules.
            .. note::
                Use ``pynext`` to listen every module.
        colored:
            Whether the debugger is supposed to use colorlog library for log coloring.
        level:
            From which level should logger listen to logs.
        file_path:
            Path to the ``.log`` file to save debugger logs.
            .. note::
                If the file path is not specified then the logs will be displayed in the console.
        """

        logger = logging.getLogger(module)
        logger.setLevel(level)

        if file_path is not None:
            logger = logging.getLogger(module)
            logger.setLevel(level)
            handler = logging.FileHandler(filename=file_path, encoding='utf-8', mode='w')
            handler.setFormatter(logging.Formatter('%(asctime)s | %(name)s | %(levelname)s > %(message)s'))
            logger.addHandler(handler)

        else:
            handler = logging.StreamHandler()
            handler.setLevel(level)

            if colored is True:
                handler.setFormatter(
                    ColoredFormatter('%(log_color)s %(asctime)s | %(name)s | %(levelname)s > %(message)s')
                )
            else:
                handler.setFormatter(logging.Formatter('%(asctime)s | %(name)s | %(levelname)s > %(message)s'))

            logger.addHandler(handler)

        return cls(logger)
