from common import *


def save_as_file(rawData: bytes, file_location: str) -> None:
    LOG_INFO(f'saving data in {file_location}')
    with open(file_location, 'wb') as f:
        f.write(rawData)
