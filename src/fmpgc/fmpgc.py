# Standard library
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import argparse
import os
import sys

# Third-party
import pandas as pd

# Local application
import jon_bulman_utilities

from enum import IntEnum

class Option(IntEnum):
    NEW_MEMBER_INVITE = 1
    JOINING_MEMBER_PAYMENT = 2
    RENEWAL_PAYMENT = 3
    MEMBER_RENEWED = 4
    MEMBER_EXPIRING = 5
    ADD_NEW_MEMBER = 6
    MEMBER_EXPIRED = 7
    TAILORED_TEMPLATE = 8

IT_OPTIONS = {Option.ADD_NEW_MEMBER, Option.MEMBER_EXPIRED, Option.TAILORED_TEMPLATE}
TREASURY_OPTIONS = {Option.JOINING_MEMBER_PAYMENT, Option.RENEWAL_PAYMENT}
MEMBERSHIP_OPTIONS = {Option.NEW_MEMBER_INVITE, Option.MEMBER_RENEWED, Option.MEMBER_EXPIRING}

OPTIONS = {
    1: "[Membership] New Member invite to join (personal details request)",
    2: "[Membership-Treasury] Payment Request (Joining member)",
    3: "[Membership-Treasury] Payment Request (Member invite to renew)",
    4: "[Membership] Member renewed",
    5: "[Membership] Member expiring",
    6: "[IT] Add new member (have paid)",
    7: "[IT] Member expired",
    8: "[IT] Tailored Template",
}

def main():
    # This ensures every time the script starts, it prints a clear timestamp
    todays_date = datetime.now(tz=ZoneInfo("Europe/London"))
    print(f"\n--- SCRIPTS STARTING: {todays_date} ---\n")

    jon_bulman_utilities.setup_environment()

    parser = argparse.ArgumentParser(description="FMPGC Email Script")
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
        default="data/settings.json"
        )
    parser.add_argument(
        "--membershipemail",
        "-m",
        help="FMPGC Membership email address",
        type=str,
        default="fmpgcmembership@gmail.com"
        )
    args = parser.parse_args()

    print(f"Config file: [{args.config_file}]")
    config_file = str(args.config_file)

    print(f"Data folder: [{args.data_folder}]")
    data_folder = str(args.data_folder)

    print(f"Membership email: [{args.membershipemail}]")
    membership_email = str(args.membershipemail)

    config = jon_bulman_utilities.Load_Config(config_file)
    if config is None:
        print("No configuration file loaded - exiting")
        return 1
    
    it_credentials   = jon_bulman_utilities.Get_Variable("GOOGLE_FMPGC_IT_CREDENTIALS",config,0)
    it_token_file    = jon_bulman_utilities.Get_Variable("GOOGLE_FMPGC_IT_TOKEN",config,0)
    membership_credentials   = jon_bulman_utilities.Get_Variable("GOOGLE_FMPGC_MEMBERSHIP_CREDENTIALS",config,0)
    membership_token_file    = jon_bulman_utilities.Get_Variable("GOOGLE_FMPGC_MEMBERSHIP_TOKEN",config,0)
    #print(f"IT Credentials: [{it_credentials}]")
    #print(f"IT Token File:[{it_token_file}]")
    #print(f"Membership Credentials: [{membership_credentials}]")
    #print(f"Membership Token File:[{membership_token_file}]")
    bcc_emails = jon_bulman_utilities.Get_Variable("FMPGC_BCC_EMAILS",config,0)
    print(f"BCC Emails: [{bcc_emails}]")
    # Check the csv file exists
    current_directory = os.getcwd()
    print(f"The current working directory is: [{current_directory}]\n")

    csv_file = data_folder+"fmpgc_members.csv"
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

    # Load the HTML templates
    template_files = {
        "expired": "membership_expired_template.html",
        "expiring": "membership_expiring_template.html",
        "new": "membership_new_template.html",
        "renewed": "membership_renewed_template.html",
        "payment_request": "membership_payment_request_template.html",
        "invite_to_renew": "membership_invite_to_renew_template.html",
        "invite_to_join": "membership_invite_to_join_template.html"
    }

    templates = {}

    try:
        for name, filename in template_files.items():
            htmlfile = Path(data_folder) / filename
            templates[name] = htmlfile.read_text(encoding="utf-8")
    except OSError as e:
        print(f"Error reading template file: [{e}]")
        sys.exit(1)

    membership_expired_template          = templates["expired"]
    membership_expiring_template         = templates["expiring"]
    membership_new_template              = templates["new"]
    membership_renewed_template          = templates["renewed"]
    membership_invite_to_renew_template  = templates["invite_to_renew"]
    membership_invite_to_join_template   = templates["invite_to_join"]
    membership_payment_request_template  = templates["payment_request"]
    print('------------- ')

    #emailCC = False
    #option = input('CC Membership Email? (non-blank is yes) -> ')
    #if option != "" :
    #    emailCC = True

    cc = None
    #if emailCC:
    #    cc = membership_email
    #    print("Emails will be CC'd to the membership email address")

    emailBCC = False
    option = input('Send Email as BCC to recipient? (non-blank is yes)? -> ')
    if option != "" :
        emailBCC = True
        print("Emails will be sent as BCC to the member, and the member will not see the email address of the sender")

    print("Options:")
    print("-------------")
    for num, text in OPTIONS.items():
        print(f"{num}. {text}")
    print("-------------")

    #onceOnly = False
    onlyOnceTemplate = False
    #invite_link = None
    subject = ""
    broadcast_template = "membership_broadcast.html"
    while ( option := input('Please select required option? >> ')) in ['0', '1', '2', '3', '4','5','6','7','8']:
        if option == '0':
            print("Exiting")
            break
        int_Option = int(option)
        if int_Option in IT_OPTIONS:    # email from IT
            credentials = it_credentials
            token_file = it_token_file
            if int_Option in [Option.MEMBER_EXPIRED, Option.ADD_NEW_MEMBER]:
                cc = membership_email
            #    print("Emails will be CC'd to the membership email address")            
        else:                           # email from membership
            credentials = membership_credentials
            token_file = membership_token_file

        for index, row in csvData.iterrows():
            name = row["Name"]
            emailAddress = row["Email"]

            if emailBCC:
                bcc = f"{emailAddress},{bcc_emails}" if int_Option == Option.ADD_NEW_MEMBER else emailAddress
                emailAddress = None
            else:
                bcc = bcc_emails if int_Option == Option.ADD_NEW_MEMBER else None
            email_body=""
            print(f"Processing:{index} name:{name} to:{emailAddress} bcc:{bcc}")
            action=True
            match int_Option:
                case Option.NEW_MEMBER_INVITE:
                    subject = "FMPGC Invitation to Join!"
                    email_body += template_edit_html(row,membership_invite_to_join_template)
                case Option.JOINING_MEMBER_PAYMENT:
                    subject = "FMPGC Membership Payment Request!"
                    email_body += template_edit_html(row,membership_payment_request_template)
                case Option.RENEWAL_PAYMENT:
                    subject = "FMPGC Membership Renewal Invitation!"
                    email_body += template_edit_html(row,membership_invite_to_renew_template)
                case Option.MEMBER_RENEWED:
                    subject = "FMPGC Membership Payment received - Welcome Back!"
                    email_body += template_edit_html(row,membership_renewed_template)
                case Option.MEMBER_EXPIRING:
                    subject = "FMPGC Membership Expiring"
                    email_body += template_edit_html(row,membership_expiring_template)
                case Option.ADD_NEW_MEMBER:
                    subject = "FMPGC Payment Received - Welcome to FMPGC!"
                    email_body += template_edit_html(row,membership_new_template)
                case Option.MEMBER_EXPIRED:
                    subject = "FMPGC Membership Expired - Sorry to see you go!"
                    email_body += template_edit_html(row,membership_expired_template)
                case Option.TAILORED_TEMPLATE:
                    tmpl = "membership_broadcast.html"
                    if onlyOnceTemplate == False:
                        tmpl = input('Enter template name (defaults to membership_broadcast.html)-> ')
                        if tmpl != "" :
                            broadcast_template = tmpl
                    try:
                        htmlfile = Path(str(data_folder)) / Path(broadcast_template)
                        tailored_template = htmlfile.read_text(encoding="utf-8")
                    except OSError as e:
                        print(f"Error reading template file: [{e}]")
                        sys.exit(1)
                    print(f"Processing:{index} name:{name} to:{emailAddress} bcc:{bcc}")
                    print(f"Template: {broadcast_template}")
                    if onlyOnceTemplate == False:
                        subject = input('Enter Subject -> ')
                    onlyOnceTemplate = True
                    if subject == "" :
                        action = False
                        print("No subject entered, skipping email")
                    else :
                        email_body += template_edit_html(row,str(tailored_template))
                        #print(f"email body {email_body}")
            if action:
                print(f"Sending email to:{name} to:{emailAddress} bcc:{bcc}")
                #input("Press Enter to continue...")
                jon_bulman_utilities.Email_Me(credentials, token_file, emailAddress, subject, email_body,cc, bcc)

def template_edit_html(row, inputhtml: str) -> str:
    body = inputhtml

    # Loop through each column name and value in the row
    for col in row.index:
        value = row[col]
        body = body.replace(f"{{{{{col}}}}}", str(value))
        #print(f"Replaced {{{{{col}}}}} with {value}")

    return body


if __name__ == "__main__":
    main()