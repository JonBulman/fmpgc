import json
import os
import sys

from dotenv import load_dotenv

from fmpgc_package import fmpgc_classes
    
def setup_environment():
    load_dotenv()

# The config file is a key file to load settings
def Load_Config(configfile):
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
        print("Config loaded ",configPath)
    else :
         print("Failed to find config ",configPath)

    return config

def Get_Variable(name,config,verbose=0):
    # can be set in
    # 1. Command line parameter
    # 2. Environment variable
    # 3. config.json file
    # My order of priority is... 1,2,3

    val = os.getenv(name)
    if val is not None and verbose > 0:
        print(f"Get_Variable: {name} from ENV VAR: {val}")
    if val is not None:
        return val
    elif config is not None:
        val = config.get(name)
        if val is not None and verbose > 0:
            print(f"Get_Variable: {name} from CONFIG FILE: {val}")
        return val
    if verbose > 0:
        print(f"Get_Variable: {name} NOT FOUND")
    return None

OPTION_TEXT = {
    fmpgc_classes.Option.EXIT: "Exit",
    fmpgc_classes.Option.NEW_MEMBER_INVITE: "[Membership] New Member invite to join (personal details request)",
    fmpgc_classes.Option.JOINING_MEMBER_PAYMENT: "[Membership-Treasury] Payment Request (Joining member)",
    fmpgc_classes.Option.RENEWAL_PAYMENT: "[Membership-Treasury] Payment Request (Member invite to renew)",
    fmpgc_classes.Option.MEMBER_RENEWED: "[Membership] Member renewed",
    fmpgc_classes.Option.MEMBER_EXPIRING: "[Membership] Member expiring",
    fmpgc_classes.Option.ADD_NEW_MEMBER: "[IT] Add new member. (Manually added to EasyTeam)",
    fmpgc_classes.Option.ADD_NEW_MEMBER_EASYTEAM: "[IT] Add new member (EasyTeam invite link)",
    fmpgc_classes.Option.MEMBER_EXPIRED: "[IT] Member expired",
    fmpgc_classes.Option.TAILORED_TEMPLATE: "[IT] Tailored Template",
}


def get_menu_option() -> fmpgc_classes.Option:
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
            option = fmpgc_classes.Option(i)
            
            #print(f"\nSelected option: {option.name}\n{OPTION_TEXT[option]}")
            return option

        except ValueError:
            # This triggers if they hit Enter without typing, or typed a letter (like 'A')
            print(f"\n[!] Error: Please enter a valid number, not '{user_input}'.")
            
        except Exception as e:
            # This triggers if they enter a number that isn't in the menu (like '9')
            print(f"\n[!] Error: Not a valid menu option {e}.")