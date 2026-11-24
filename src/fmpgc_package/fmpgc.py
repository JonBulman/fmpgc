# Standard library
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import argparse
import os
import sys
import time

# Third-party
import pandas as pd

from fmpgc_package import config_utils, setup_environment

from fmpgc_package import send_email
from fmpgc_package import get_menu_option
from fmpgc_package import fmpgc_classes

def main():
    # This ensures every time the script starts, it prints a clear timestamp
    todays_date = datetime.now(tz=ZoneInfo("Europe/London"))
    print(f"\n--- SCRIPTS STARTING: {todays_date} ---\n")

    setup_environment()

    parser = argparse.ArgumentParser(description="FMPGC Membership Communication & Administration System")
    parser.add_argument(
        "--data-folder",
        "-d",
        help="Data folder location",
        type=str,
        default="data/"
        )
    parser.add_argument(
        "--config-file",
        "-c",
        help="Location of the config file",
        type=str,
        default="data/fmpgc_settings.json"
        )
    parser.add_argument(
        "--csv-file",
        "-csv",
        help="Location of the CSV file",
        type=str,
        default="data/fmpgc_members.csv"
        )    
    args = parser.parse_args()

    print(f"Config file: [{args.config_file}]")
    config_file = str(args.config_file)

    print(f"Data folder: [{args.data_folder}]")
    data_folder = str(args.data_folder)

    print(f"CSV file: [{args.csv_file}]")
    csv_file = str(args.csv_file)

    config = config_utils.load_config(config_file)
    if config is None:
        print("No configuration file loaded - exiting")
        return 1
    
    it_credentials   = config_utils.get_variable("GOOGLE_FMPGC_IT_CREDENTIALS",config)
    it_token_file    = config_utils.get_variable("GOOGLE_FMPGC_IT_TOKEN",config)
    membership_credentials   = config_utils.get_variable("GOOGLE_FMPGC_MEMBERSHIP_CREDENTIALS",config)
    membership_token_file    = config_utils.get_variable("GOOGLE_FMPGC_MEMBERSHIP_TOKEN",config)
    
    fmpgc_it_email = config_utils.get_variable("FMPGC_IT_EMAIL",config)
    fmpgc_membership_email = config_utils.get_variable("FMPGC_MEMBERSHIP_EMAIL",config)
    bcc_emails = config_utils.get_variable("FMPGC_BCC_EMAILS",config)
    print(f"BCC Emails: [{bcc_emails}]")
    # Check the csv file exists
    current_directory = os.getcwd()
    print(f"The current working directory is: [{current_directory}]\n")

    try:
        csvData = pd.read_csv(csv_file, encoding="cp1252")
    except OSError as e:
        print(f"Error reading CSV file: [{e}]")
        sys.exit(1)

    if csvData is None:
        print(f"Error loading CSV data, exiting {csv_file}")
        sys.exit(1)
    else:
        # remove any blank rows
        csvData = csvData.dropna(how="all")

        required_columns = {"Name", "Email", "Invite Link"}
        missing_columns = required_columns - set(csvData.columns)

        if missing_columns:
            print(
                f"CSV is missing required columns: {', '.join(sorted(missing_columns))}"
            )
            sys.exit(1)

        for index, row in csvData.iterrows():
            name = row["Name"]
            email_address = row["Email"]

            print(
                f"CSV Loaded: [{index}] Name: [{name}] Email: [{email_address}]"
            )

        column_names = csvData.columns.tolist()
        print(
            f"\nThe following {len(column_names)} names may be used as variables "
            f"in the html templates\n{column_names}\n"
            f"e.g. {{{{Name}}}} will be replaced with that row/column contents\n"
        )

    templates = config_utils.load_templates(data_folder)

    print('------------- ')

    cc = None
    emailBCC = False
    option = input('Send Email as BCC to recipient? (non-blank is yes)? -> ')
    if option != "" :
        emailBCC = True
        print("Emails will be sent as BCC to the member, and the member will not see the email address of the sender")

    # setup message log
    message_log = config_utils.SystemMonitor()

    #onceOnly = False
    onlyOnceTemplate = False
    #invite_link = None
    subject = ""
    attachment = ""
    broadcast_template = "membership_broadcast.html"

    while True:
        option = get_menu_option()
        if option == fmpgc_classes.Option.EXIT:
            print("Goodbye")
            break

        if option in fmpgc_classes.IT_OPTIONS:    # email from IT
            #print("Emails will be sent from the IT email address")
            credentials = it_credentials
            token_file = it_token_file
            from_email = fmpgc_it_email
            if option in fmpgc_classes.CC_MEMBERSHIP_OPTIONS:
                cc = fmpgc_membership_email
            #    print("Emails will be CC'd to the membership email address")            
        else:                           # email from membership
            #print("Emails will be sent from the Membership email address")
            from_email = fmpgc_membership_email
            credentials = membership_credentials
            token_file = membership_token_file

        count = 0
        for index, row in csvData.iterrows():
            name = row["Name"]
            emailAddress = row["Email"]
            membershipType = row["Membership Type"]

            if emailBCC:
                if option in (fmpgc_classes.Option.ADD_NEW_MEMBER, fmpgc_classes.Option.ADD_NEW_MEMBER_EASYTEAM):
                    bcc = f"{emailAddress},{bcc_emails}"
                else:
                    bcc = emailAddress
                emailAddress = None
            else:
                if (
                    membershipType not in ("Concessionary (FXU)", "")
                    and option in (fmpgc_classes.Option.ADD_NEW_MEMBER, fmpgc_classes.Option.ADD_NEW_MEMBER_EASYTEAM)
                ):
                    bcc = bcc_emails
                else:
                    bcc = None
            email_body=""
            count += 1
            if count%60 == 0:
                time.sleep(60)  # Sleep for 60 seconds after every 60 emails - this is to avoid hitting the Gmail API rate limit

            action=True
            if option == fmpgc_classes.Option.TAILORED_TEMPLATE:
                template = fmpgc_classes.OPTION_DEFINITIONS[option.value][3]                
                tmpl = templates[template]
                if onlyOnceTemplate == False:
                    txt = f'Enter template text (defaults to {template})-> '
                    tmpl = input(txt)
                    if tmpl != "" :
                        broadcast_template = tmpl
                if (broadcast_template not in templates) and (onlyOnceTemplate == False):
                    print(f"Loading template: {broadcast_template}")
                    try:
                        htmlfile = Path(str(data_folder)) / Path(broadcast_template)
                        tailored_template = htmlfile.read_text(encoding="utf-8")
                    except OSError as e:
                        print(f"Error reading template file: [{e}]")
                        sys.exit(1)
                else:
                    tailored_template = templates[template]
                if onlyOnceTemplate == False:
                    subject = fmpgc_classes.OPTION_DEFINITIONS[option.value][2]   
                    txt = f'Enter subject text (defaults to {subject})-> '
                    entered_subject = input(txt)
                    subject = entered_subject if entered_subject != "" else subject
                    attachment = input('Enter Attachment (blank for none) -> ')                        
                onlyOnceTemplate = True
                #if subject == "" :
                #    action = False
                #    print("No subject entered, skipping email")
                #else :
                email_body += config_utils.template_edit_html(row,str(tailored_template))
                    #print(f"email body {email_body}")
            else:
                subject = fmpgc_classes.OPTION_DEFINITIONS[option.value][2]
                template = fmpgc_classes.OPTION_DEFINITIONS[option.value][3]
                email_body += config_utils.template_edit_html(row,templates[template])

            if action:
                email_result=send_email(credentials, token_file, emailAddress, subject, email_body,cc, bcc, attachment)

                fromcc = f"from:{from_email}"
                if cc:
                    fromcc += f" cc:{cc}"
                if bcc:
                    fromcc += f" bcc:{bcc}"

                message_log.messagelog(
                    str(emailAddress),
                    fromcc,
                    action=option.name,
                    result=email_result
                )
        print(f"Processed {count} emails for option: {option.name}\n")


if __name__ == "__main__":
    main()