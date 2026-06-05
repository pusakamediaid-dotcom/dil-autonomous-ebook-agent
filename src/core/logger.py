"""
DIL Autonomous Ebook Agent - Logger Module

Provides secure logging with API key masking and automatic output directory creation.
"""

import logging
import re
import os
import sys
from pathlib import Path
from typing import Optional

# Pattern to detect potential API keys
API_KEY_PATTERN = re.compile(
    r'(sk-[a-zA-Z0-9]{20,}|'
    r'[a-zA-Z0-9_-]{40,}|'
    r'AIza[a-zA-Z0-9_-]{35}|'
    r'[a-zA-Z0-9_-]{40,}--[a-zA-Z0-9_-]{20,})'
)

# Pattern for Bearer tokens
BEARER_TOKEN_PATTERN = re.compile(r'Bearer\s+[a-zA-Z0-9_-]{20,}', re.IGNORECASE)


class MaskingFilter(logging.Filter):
    """
    Logging filter that masks sensitive information like API keys.
    Prevents accidental logging of secrets.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and mask sensitive data in log record."""
        if isinstance(record.msg, str):
            record.msg = self._mask_secrets(record.msg)
        
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: self._mask_secrets(str(v)) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    self._mask_secrets(str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )
        
        return True
    
    def _mask_secrets(self, text: str) -> str:
        """Mask secrets in text string."""
        # Mask API keys (sk-... etc)
        text = API_KEY_PATTERN.sub(lambda m: f"[API_KEY_MASKED:{len(m.group())}]", text)
        
        # Mask Bearer tokens
        text = BEARER_TOKEN_PATTERN.sub("[BEARER_TOKEN_MASKED]", text)
        
        # Mask long alphanumeric strings that look like keys
        long_key_pattern = re.compile(r'[a-zA-Z0-9_-]{50,}')
        text = long_key_pattern.sub("[LONG_STRING_MASKED]", text)
        
        return text


def get_logger(
    name: str = "dil_agent",
    log_file: str = "output/error_log.txt",
    level: int = logging.INFO
) -> logging.Logger:
    """
    Get a configured logger with file and console handlers.
    
    Args:
        name: Logger name, typically module name.
        log_file: Path to log file, relative to project root.
        level: Logging level (default: INFO).
    
    Returns:
        Configured logging.Logger instance.
    
    Example:
        >>> logger = get_logger("router_agent")
        >>> logger.info("Processing request")
    """
    # Create output directory if not exists
    output_dir = Path(log_file).parent
    if output_dir != Path('.'):
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(levelname)-8s | %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(MaskingFilter())
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(MaskingFilter())
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_secret_detected(logger: logging.Logger, context: str) -> None:
    """Log that a potential secret was detected and masked."""
    logger.warning(f"Secret-like pattern detected and masked in: {context}")


def log_safe(logger: logging.Logger, message: str, level: str = "info") -> None:
    """
    Safely log a message ensuring no secrets are exposed.
    
    Args:
        logger: Logger instance.
        message: Message to log.
        level: Log level ('debug', 'info', 'warning', 'error').
    """
    masking_filter = MaskingFilter()
    safe_message = masking_filter._mask_secrets(message)
    
    if level == "debug":
        logger.debug(safe_message)
    elif level == "info":
        logger.info(safe_message)
    elif level == "warning":
        logger.warning(safe_message)
    elif level == "error":
        logger.error(safe_message)