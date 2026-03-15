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
import os,tracemalloc,csv,time
from datetime import datetime
from typing import Any


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

def filter_snapshot(snapshot: tracemalloc.Snapshot, include_stdlib: bool) -> tracemalloc.Snapshot:
    filters = [
        tracemalloc.Filter(False, "<unknown>"),
    ]

    if not include_stdlib:
        filters.extend(
            [
                tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
                tracemalloc.Filter(False, "<frozen importlib._bootstrap_external>"),
            ]
        )

    return snapshot.filter_traces(filters)

def take_absolute_records(snapshot: tracemalloc.Snapshot,timestamp_sec: float,) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for stat in snapshot.statistics("filename"):
        frame = stat.traceback[0]
        rows.append(
            {
                "time_sec": timestamp_sec,
                "file": frame.filename,
                "memory_mb": stat.size,
                "alloc_count": stat.count,
            }
        )
    return rows

def append_memory_absolute_csv(output_file,interval=30):
    """
    Continuously sample Python memory allocations and append absolute values to a CSV file.

    Parameters
    ----------
    output_file : str
        CSV file to append samples
    interval : int
        sampling interval in seconds
    nframe : int
        tracemalloc stack depth
    """
    file_exists = os.path.exists(output_file)
    with open(output_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "file", "memory_mb", "alloc_count"])
        start = time.time()
        while True:
            snapshot = tracemalloc.take_snapshot()

            snapshot = snapshot.filter_traces((
                tracemalloc.Filter(False, "<unknown>"),
                tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
            ))
            stats = snapshot.statistics("filename")
            timestamp = time.time()
            for stat in stats:
                frame = stat.traceback[0]
                writer.writerow([timestamp,frame.filename,stat.size/(1024 * 1024),stat.count])
            f.flush()
            time.sleep(interval)