"""Centralized Application Logging Infrastructure with Sensitive Data Redaction (CF-04)."""

import re
import sys
import logging
from shared.config import settings


class SensitiveDataFilter(logging.Filter):
    """Filter that intercepts and masks credentials, tokens, and API keys from logs."""

    PATTERNS = [
        (re.compile(r'(password[\'"]?\s*[:=]\s*[\'"]?)([^\s,\'"}]+)([\'"]?)', re.IGNORECASE), r'\1***REDACTED***\3'),
        (re.compile(r'(Bearer\s+)([A-Za-z0-9\-_.~+/]+=*)', re.IGNORECASE), r'\1***REDACTED***'),
        (re.compile(r'(sk-[A-Za-z0-9_-]{20,})', re.IGNORECASE), r'sk-***REDACTED***'),
        (re.compile(r'(gsk_[A-Za-z0-9_-]{20,})', re.IGNORECASE), r'gsk_***REDACTED***'),
        (re.compile(r'(AIza[0-9A-Za-z-_]{35})', re.IGNORECASE), r'AIza***REDACTED***'),
        (re.compile(r'(secret_key[\'"]?\s*[:=]\s*[\'"]?)([^\s,\'"}]+)([\'"]?)', re.IGNORECASE), r'\1***REDACTED***\3'),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, repl in self.PATTERNS:
                record.msg = pattern.sub(repl, record.msg)
        return True


def setup_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
        )
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveDataFilter())
        logger.addHandler(handler)

    return logger


logger = setup_logger()
get_logger = setup_logger
