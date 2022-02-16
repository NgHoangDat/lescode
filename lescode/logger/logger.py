import asyncio
import functools
import logging
from logging.handlers import RotatingFileHandler
from logging import Handler, StreamHandler
import os
import time
from typing import *
from typing import Callable

FORMATTER = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(filename)s.%(funcName)s:%(lineno)i] %(message)s",
    "%Y-%m-%d %H:%M:%S",
)


@functools.lru_cache(typed=True)
def init_logger(
    name: str,
    log_dir: Optional[str] = None,
    max_bytes: int = 10000000,
    backup_count: int = 5,
    level: int = logging.INFO,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    add_handler(logger, StreamHandler())

    if log_dir is not None:
        os.makedirs(log_dir, exist_ok=True)
        log_filename = os.path.join(log_dir, f"{name}.out")
        add_handler(
            logger,
            RotatingFileHandler(
                log_filename, maxBytes=max_bytes, backupCount=backup_count
            ),
        )

    return logger


def add_handler(
    logger: logging.Logger,
    *handlers: List[Handler],
    formatter: logging.Formatter = FORMATTER,
):
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def log_error(
    _func: Optional[Callable] = None,
    logger: Optional[logging.Logger] = None,
    return_value: Any = None,
    swallow_err: bool = False,
    **options,
):

    if logger is None:
        logger = logging.getLogger()

    def decorator(func: Callable):

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    res = await func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"{func.__name__}: {e}")
                    if swallow_err:
                        return return_value
                    else:
                        raise e
                else:
                    return res

        else:

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    res = func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"{func.__name__}: {e}")
                    if swallow_err:
                        return return_value
                    else:
                        raise e
                else:
                    return res

        return wrapper

    if _func:
        return decorator(_func)

    return decorator


def log_time(
    _func: Optional[Callable] = None, logger: Optional[logging.Logger] = None, **options
):

    if logger is None:
        logger = logging.getLogger()

    def decorator(func: callable):

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start = time.time()
                res = await func(*args, **kwargs)
                end = time.time()
                logger.info(f"{func.__name__}: {end - start}")
                return res

        else:

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                res = func(*args, **kwargs)
                end = time.time()
                logger.info(f"{func.__name__}: {end - start}")
                return res

        return wrapper

    if _func:
        return decorator(_func)

    return decorator
