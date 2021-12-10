from logger import LOG_ERROR, LOG_INFO


def panic(err_message: str = "panic!") -> None:
    LOG_ERROR(err_message)
    exit(1)
