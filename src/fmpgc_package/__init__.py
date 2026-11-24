"""
Common utilities.
"""

from .config_utils import load_config, get_variable, setup_environment,get_menu_option
from .email_utils import send_email

__version__ = "0.1.0"

__all__ = [
    "load_config",
    "get_variable",
    "send_email",
    "setup_environment",
    "get_menu_option"
]