from logger import LOG_INFO
from logger import LOG_ERROR

def panic(err_message: str = 'panic!') -> None:
    LOG_ERROR(err_message)
    exit(1)
