"""
Qualitative Assessment and Application of CTI based on Reinforcement Learning.
    Copyright (C) 2026  Georgios Sakellariou

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import logging.handlers
import os
from datetime import datetime


def create_logger(
        name: str,
        config: dict = None,
        json_format: bool = False
) -> logging.Logger:
    """
    Creates a reusable logger with:
    - Rotating file handler
    - Optional JSON formatting
    """
    log_dir = config["logs_dir"]
    os.makedirs(log_dir, exist_ok=True)
    if config['log_level'] == "info":
        level = logging.INFO
    elif config['log_level'] == "debug":
        level = logging.DEBUG
    elif config['log_level'] == "warning":
        level = logging.WARNING
    elif config['log_level'] == "error":
        level = logging.ERROR
    else:
        level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    if logger.handlers:
        return logger  # Prevent duplicate handlers

    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{name}_{timestamp}.log")

    # File handler (10MB per file, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )

    if json_format:
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
        )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
