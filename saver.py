from typing import List

from common import *


def save_as_file(raw_data: bytes, file_location: str) -> None:
    LOG_INFO(f"saving data in {file_location}")
    with open(file_location, "wb") as f:
        f.write(raw_data)
