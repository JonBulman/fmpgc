import time
import json
import logging

from enum import IntEnum

class Option(IntEnum):
    EXIT = 0
    NEW_MEMBER_INVITE = 1
    JOINING_MEMBER_PAYMENT = 2
    RENEWAL_PAYMENT = 3
    MEMBER_RENEWED = 4
    MEMBER_EXPIRING = 5
    ADD_NEW_MEMBER = 6
    ADD_NEW_MEMBER_EASYTEAM = 7
    MEMBER_EXPIRED = 8
    TAILORED_TEMPLATE = 9

OPTION_TEXT = {
    Option.EXIT: "Exit",
    Option.NEW_MEMBER_INVITE: "[Membership] New Member invite to join (personal details request)",
    Option.JOINING_MEMBER_PAYMENT: "[Membership-Treasury] Payment Request (Joining member)",
    Option.RENEWAL_PAYMENT: "[Membership-Treasury] Payment Request (Member invite to renew)",
    Option.MEMBER_RENEWED: "[Membership] Member renewed",
    Option.MEMBER_EXPIRING: "[Membership] Member expiring",
    Option.ADD_NEW_MEMBER: "[IT] Add new member. (Manually added to EasyTeam)",
    Option.ADD_NEW_MEMBER_EASYTEAM: "[IT] Add new member (EasyTeam invite link)",
    Option.MEMBER_EXPIRED: "[IT] Member expired",
    Option.TAILORED_TEMPLATE: "[IT] Tailored Template",
}

class IT_OPTIONS(IntEnum):
    ADD_NEW_MEMBER = 6
    ADD_NEW_MEMBER_EASYTEAM = 7
    MEMBER_EXPIRED = 8
    TAILORED_TEMPLATE = 9

class MEMBERSHIP_OPTIONS(IntEnum):
    NEW_MEMBER_INVITE = 1
    JOINING_MEMBER_PAYMENT = 2
    RENEWAL_PAYMENT = 3
    MEMBER_RENEWED = 4
    MEMBER_EXPIRING = 5

class CC_MEMBERSHIP_OPTIONS(IntEnum):
    ADD_NEW_MEMBER = 6
    ADD_NEW_MEMBER_EASYTEAM = 7
    MEMBER_EXPIRED = 8
    
def get_menu_option() -> Option:
    while True:  # Keep looping until they give a valid answer
        print("\nOptions:")
        print("-------------")

        for option, description in OPTION_TEXT.items():
            print(f"{option.value}. {description}")

        print("-------------")

        user_input = input("Select option: ")
        
        try:
            # Try to convert their input to a number
            i = int(user_input)
            
            # Try to match it to a valid Option
            option = Option(i)
            
            #print(f"\nSelected option: {option.name}\n{OPTION_TEXT[option]}")
            return option

        except ValueError:
            # This triggers if they hit Enter without typing, or typed a letter (like 'A')
            print(f"\n[!] Error: Please enter a valid number, not '{user_input}'.")
            
        except Exception as e:
            # This triggers if they enter a number that isn't in the menu (like '9')
            print(f"\n[!] Error: Not a valid menu option {e}.")


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