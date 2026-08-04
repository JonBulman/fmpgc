# Imports
import argparse
import base64
from datetime import datetime
import os
import pandas as pd
import sys
from zoneinfo import ZoneInfo

import jon_bulman_utilities

#def resourcePath(filename):
#    if getattr(sys, 'frozen', False):
#        # Running as compiled .exe
#        return os.path.join(os.path.dirname(sys.executable), filename)
#    else:
#        # Running as .py script
#        return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

def main():
    # This ensures every time the script starts, it prints a clear timestamp
    todays_date = datetime.now(tz=ZoneInfo("Europe/London"))
    print(f"\n--- SCRIPTS STARTING: {todays_date} ---\n")

    jon_bulman_utilities.setup_environment()

    parser = argparse.ArgumentParser(description="FMPGC Email Script")
    parser.add_argument(
        "--config-file",
        "-c",
        help="Path to the config file (default: settings.json)",
        type=str,
        default="settings.json"
)
    args = parser.parse_args()

    print(f"Config file: str({args.config_file})")
    config_file = str(args.config_file)

    config = jon_bulman_utilities.Load_Config(config_file)
    if config is None:
        print("No configuration file loaded - exiting")
        return 1
    
    credentials   = jon_bulman_utilities.Get_Variable("GOOGLE_FMPGC_CREDENTIALS",config,0)
    token_file    = jon_bulman_utilities.Get_Variable("GOOGLE_FMPGC_TOKEN",config,0)

    print("Credentials:",credentials)
    print("Token File:",token_file)

    # Check the csv file exists
    current_directory = os.getcwd()
    print("The current working directory is:", current_directory)

    csv_file = jon_bulman_utilities.Get_Variable("FMPGC_CSV_FILE",config,0)
    fmpgc_membership_email = jon_bulman_utilities.Get_Variable("FMPGC_MEMBERSHIP_EMAIL",config,0)
    fmpgc_it_email = jon_bulman_utilities.Get_Variable("FMPGC_IT_EMAIL",config,0)
    fmpgc_website = jon_bulman_utilities.Get_Variable("FMPGC_WEBSITE",config,0)
    fmpgc_invite_link = jon_bulman_utilities.Get_Variable("FMPGC_INVITE_LINK",config,0)
    fmpgc_members_area = jon_bulman_utilities.Get_Variable("FMPGC_MEMBERS_AREA",config,0)
    fmpgc_shed_code = jon_bulman_utilities.Get_Variable("FMPGC_SHED_CODE",config,0)
    fmpgc_group_email = jon_bulman_utilities.Get_Variable("FMPGC_GROUP_EMAIL",config,0)
    fmpgc_whatsapp_group_link = jon_bulman_utilities.Get_Variable("FMPGC_WHATSAPP_GROUP_LINK",config,0)
    easyTeam_apple=jon_bulman_utilities.Get_Variable("FMPGC_EASYTEAM_APPLE",config,0)
    easyTeam_android=jon_bulman_utilities.Get_Variable("FMPGC_EASYTEAM_ANDROID",config,0)
    fmpgc_membership_renewal_link = jon_bulman_utilities.Get_Variable("FMPGC_MEMBERSHIP_RENEWAL_LINK",config,0)
    fmpgc_image_name = jon_bulman_utilities.Get_Variable("FMPGC_IMAGE",config,0)

    fmpgc_logo = fmpgc_image_src =""
    if fmpgc_image_name:
        fmpgc_logo = Load_image_as_base64(fmpgc_image_name)
    if fmpgc_logo != "":
       fmpgc_image_src = (
                f"<div style='text-align:center;'>"
                f"<img src=\"{fmpgc_logo}\" alt='Flushing & Mylor Pilot Gig Club' />"
                f"</div>"
            )
    try:
        csvData = pd.read_csv(str(csv_file))
    except Exception as e:
        print("Error reading CSV file:", e)
        sys.exit(1)

    if csvData is None:
        print("Error loading CSV data, exiting")
        sys.exit(1)
    else:
        for index, row in csvData.iterrows():
            name = row["Name"]
            emailAddress = row["Email"]
            print("Loaded:", index, " name ", name, "email address", emailAddress)

    print('------------- ')

    emailCC = False
    option = input('EmailCC? (1=True,0=False) -> ')
    if option == "" :
        option=0
    if int(option) == 1 :
        emailCC = True

    cc = None
    if emailCC:
        cc = fmpgc_membership_email

    print('Options: \n'+'------------- \n'+
        '1. Add new member\n'
        '2. Member expiration\n'
        '3. Member expired\n'
        '4. Member renewal\n'
        )
    print('------------- ')

    while ( option := input('Please select required option? >> ')) in ['0', '1', '2', '3', '4']:
        if option == '0':
            print("Exiting")
            break
        int_Option = int(option)

        for index, row in csvData.iterrows():
            name = row["Name"]
            emailAddress = row["Email"]
            #print("Processing:",index," name ",name,"email address",emailAddress)
            email_body = email_header(fmpgc_image_src)
            subject = ""
            match int_Option:
                case 1:
                    subject = "Welcome to FMPGC!"
                    email_body += fmpgc_new_member_email(name,fmpgc_invite_link,fmpgc_shed_code, fmpgc_group_email)
                case 2:
                    subject = "FMPGC Membership Expiring"
                    email_body += fmpgc_membership_expiring_email(name, fmpgc_membership_renewal_link, fmpgc_membership_email)
                case 3:
                    subject = "FMPGC Membership Expired - Sorry to see you go!"
                    email_body = fmpgc_membership_expired_email(name, fmpgc_membership_renewal_link, fmpgc_membership_email)
                case 4:
                    subject = "FMPGC Membership Renewal - Welcome Back!"
                    email_body += fmpgc_membership_renewal_email(name, easyTeam_apple, easyTeam_android, fmpgc_shed_code, fmpgc_group_email)

            email_body += email_footer(fmpgc_membership_email,fmpgc_it_email)     
            match int_Option:
                case 1 | 4:
                    email_body += fmpgc_clubs_links(fmpgc_website, fmpgc_members_area, fmpgc_whatsapp_group_link, fmpgc_membership_email)
                case _:
                    pass

            jon_bulman_utilities.Email_Me(credentials, token_file, emailAddress, subject, email_body,cc)

def email_header(fmpgc_image_src):
    body = (
        f"{fmpgc_image_src}<br><br>"
    )
    return body

def email_footer(fmpgc_membership_email,fmpgc_it_email):
    body = (
        f"This is an automated email.<br><br>"
        f"Best regards,<br>FMPGC IT<br>{fmpgc_it_email}<br><br>"
    )
    return body

def fmpgc_new_member_email(name, fmpgc_invite_link, fmpgc_shed_code, fmpgc_group_email):
    break_line = "<br>"
    body = (
        f"Dear {bold('green', name)}{break_line}{break_line}"
        f"{bold('green', 'Welcome to FMPGC!')}{break_line}{break_line}"
        f"We use the {bold('black', 'EasyTeam')} app for managing rowing sessions.{break_line}{break_line}"
        f"Please use this <b><a href={fmpgc_invite_link}>link</a></b> to access your account.{break_line}{break_line}"      
        f"You should also receive an invitation to join the club email group {fmpgc_group_email}. If you accept this, you will receive club-wide emails we send out.{break_line}{break_line}"
        f"The padlock code for both the upper and lower gig shed is {bold('blue', fmpgc_shed_code)}.{break_line}{break_line}"        
       )
    return body

def fmpgc_clubs_links(fmpgc_website, fmpgc_members_area, fmpgc_whatsapp_group_link, fmpgc_membership_email):        
    break_line = "<br>"
    body = (
        f"<b>Useful Resources</b>{break_line}{break_line}"
        f"You can find our website <a href={fmpgc_website}>here</a>. Within this you will see the <a href={fmpgc_members_area}>Members Area</a>.{break_line}{break_line}"
        f"You can join the clubs WhatsApp group <a href={fmpgc_whatsapp_group_link}>here</a>.{break_line}{break_line}"
        f"If you have any membership related questions please contact {fmpgc_membership_email}.<br><br>"
    )
    return body

def fmpgc_membership_expiring_email(name, membership_renewal_link, fmpgc_membership_email):
    break_line = "<br>"
    body = (
        f"Dear {bold('orange', name)}{break_line}{break_line}"
        f"{bold('orange', 'Your membership has expired. Is this intentional?')}{break_line}{break_line}"
        f"You can renew your membership at any time by clicking <a href={membership_renewal_link}>here</a>.{break_line}{break_line}"
        f"Should you decide not to re-join before 31st July, access to the club and EasyTeam will be removed.{break_line}{break_line}"
        f"If you have any membership related questions please contact {fmpgc_membership_email}.<br><br>"
    )
    return body

def fmpgc_membership_expired_email(name, membership_renewal_link, fmpgc_membership_email):
    break_line = "<br>"
    body = (
        f"Dear {bold('red', name)}{break_line}{break_line}"
        f"{bold('red', 'Your membership has expired.')}{break_line}{break_line}"
        f"FMPGC would like to thank you for your membership and we are sorry you are leaving us.{break_line}{break_line}"
        f"You have been removed from EasyTeam, the club email group fmpgc@googlegroups.com and from the WhatsApp groups.{break_line}{break_line}"
        f"If this was not your intention please renew your membership at any time by clicking <a href={membership_renewal_link}>here</a>"
        f" or drop me a line at {fmpgc_membership_email}.<br><br>"
    )  
    return body

def fmpgc_membership_renewal_email(name, easyTeam_apple, easyTeam_android, fmpgc_shed_code, fmpgc_group_email):
    break_line = "<br>"
    body = (
        f"Dear {bold('green', name)}{break_line}{break_line}"
        f"{bold('green', 'Your FMPGC membership has been reactivated.')}{break_line}{break_line}"
        f"{bold('green', 'Welcome back!')}{break_line}{break_line}"
        f"We use the {bold('black', 'EasyTeam')} app for managing rowing sessions.{break_line}{break_line}"
        f"Download the {bold('blue', 'iPhone/iPad version:')} <a href={easyTeam_apple}>here</a> "
        f"or the {bold('blue', 'Android version:')} <a href={easyTeam_android}>here</a>.{break_line}{break_line}" 
        f"On first login, you will need our Club ID {bold('blue', '712')} using your existing EasyTeam email address and password.{break_line}{break_line}"
        f"You should also receive an invitation to rejoin the club email group {fmpgc_group_email}. If you accept this, you will receive club-wide emails we send out.{break_line}{break_line}"
        f"The padlock code for both the upper and lower gig shed is {bold('blue', fmpgc_shed_code)}.{break_line}{break_line}"        
    )

    return body

def bold(colour, value):
    return f'<b style="color:{colour};">{value}</b>'

def Load_image_as_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return ""

if __name__ == "__main__":
    main()