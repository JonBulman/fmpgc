import json
import os
import sys
from pathlib import Path
import time

import logging
# Third-party
import pandas as pd

from dotenv import load_dotenv

from fmpgc_package import fmpgc_classes
    
def setup_environment():
    load_dotenv()

# The config file is a key file to load settings
def load_config(configfile):
    if getattr(sys, 'frozen', False):
        # Running as compiled .exe
        configPath = os.path.join(os.path.dirname(sys.executable), configfile)
    else:
        # Running as .py script
            cwd = os.getcwd()
            #cwf =os.path.dirname(os.path.abspath(__file__)) # where the exe is running
            #print(cwd)
            #print(cwf)
            configPath = os.path.join(cwd, configfile)

    config=None
    ok=os.path.isfile(configPath)
    if ok :
        with open(configPath, "r") as f:
            config = json.load(f)
        print(f"Config loaded: [{configPath}]")
    else :
         print(f"Failed to find config: [{configPath}]")

    return config


def get_variable(name, config=None):
    """
    Return a configuration value as a string.

    Order of precedence:
    1. Environment variable
    2. Configuration dictionary
    3. Empty string
    """
    return str(
        os.getenv(name)
        or (config.get(name) if config else "")
        or ""
    )


def get_menu_option() -> fmpgc_classes.Option:
    while True:  # Keep looping until they give a valid answer
        print("\nOptions:")
        print("-------------")

        for item in fmpgc_classes.OPTION_DEFINITIONS:
            option = item[1]
            description = item[0]
            print(f"{option.value}. {description}")
 
        print("-------------")

        user_input = input("Select option: ")
        
        try:
            # Try to convert their input to a number
            i = int(user_input)
            
            # Try to match it to a valid Option
            option = fmpgc_classes.Option(i)
            
            #print(f"\nSelected option: {option.name}\n{fmpgc_classes.OPTION_DEFINITIONS[option.value][0]}")
            return option

        except ValueError:
            # This triggers if they hit Enter without typing, or typed a letter (like 'A')
            print(f"\n[!] Error: Please enter a valid number, not '{user_input}'.")
            
        except Exception as e:
            # This triggers if they enter a number that isn't in the menu (like '9')
            print(f"\n[!] Error: Not a valid menu option {e}.")

def load_templates(data_folder: str) -> dict:
    templates = {}
    try:
        for items in fmpgc_classes.OPTION_DEFINITIONS:
            template_name = items[3] # name of the template file
            if template_name is not None:
                htmlfile = Path(data_folder) / template_name
                templates[template_name] = htmlfile.read_text(encoding="utf-8")
                #print(f"Option {items[1].value}: Loaded template: {template_name}")
    except OSError as e:
        print(f"Error reading template file: [{e}]")
        sys.exit(1)
    return templates

def template_edit_html(row: pd.Series, inputhtml: str) -> str:
    """Replace {{ColumnName}} placeholders in the HTML template with row values."""
    body = inputhtml
    for col in row.index:
        value = row[col]
        replacement = "" if pd.isna(value) else str(value)
        body = body.replace(f"{{{{{col}}}}}", replacement)
    return body

class SystemMonitor:
    def messagelog(self, to: str, message: str, action: str, result: str) -> None:
        # 3. Structure all your data, including standard log metadata, as a dictionary
        log_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "logger_name": logger.name,
            "level": "INFO",
            "to": to,
            "action": action,
            "result": result,
            "message": message
        }
        print(f"Log: {to} | Action: {action} | Result: {result} | Message: {message}")
        
        # 4. Convert the dictionary to a JSON string and log it using your custom logger
        logger.info(json.dumps(log_data))
        #input("Press Enter to continue...")  # Pause for user input

# 1. Configure logging to only output the raw message, and save to a JSON lines file
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('fmpgc_logs.jsonl', mode='a'), # Save to file
        #logging.StreamHandler()                             # Also print to console (optional)
    ]
)

# 2. Create the custom logger to satisfy the linter
logger = logging.getLogger(__name__)