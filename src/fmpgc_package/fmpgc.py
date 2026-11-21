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

from fmpgc_package import setup_environment
from fmpgc_package import Load_Config
from fmpgc_package import Get_Variable
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

    print(f"CSV file: [{args.csv_file}]")
    csv_file = str(args.csv_file)

    print(f"Membership email: [{args.membershipemail}]")
    membership_email = str(args.membershipemail)

    config = Load_Config(config_file)
    if config is None:
        print("No configuration file loaded - exiting")
        return 1
    
    it_credentials   = Get_Variable("GOOGLE_FMPGC_IT_CREDENTIALS",config,0)
    it_token_file    = Get_Variable("GOOGLE_FMPGC_IT_TOKEN",config,0)
    membership_credentials   = Get_Variable("GOOGLE_FMPGC_MEMBERSHIP_CREDENTIALS",config,0)
    membership_token_file    = Get_Variable("GOOGLE_FMPGC_MEMBERSHIP_TOKEN",config,0)
    
    fmpgc_it_email = Get_Variable("FMPGC_IT_EMAIL",config,0)
    fmpgc_membership_email = Get_Variable("FMPGC_MEMBERSHIP_EMAIL",config,0)
    bcc_emails = Get_Variable("FMPGC_BCC_EMAILS",config,0)
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

    # Load the HTML templates
    template_files = {
        "expired": "membership_expired_template.html",
        "expiring": "membership_expiring_template.html",
        "new": "membership_add_new_member_template.html",
        "new_easyteam": "membership_add_new_member_easyteam_invite_template.html",
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
    membership_add_new_member_template   = templates["new"]
    membership_add_new_member_easyteam_invite_template = templates["new_easyteam"]
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

    # setup message log
    message_log = fmpgc_classes.SystemMonitor()

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
                cc = membership_email
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

            #print(f"Processing:{index} name:{name} to:{emailAddress} bcc:{bcc}")
            action=True
            match option:
                case fmpgc_classes.Option.NEW_MEMBER_INVITE:
                    subject = "FMPGC Invitation to Join!"
                    email_body += template_edit_html(row,membership_invite_to_join_template)
                case fmpgc_classes.Option.JOINING_MEMBER_PAYMENT:
                    subject = "FMPGC Membership Payment Request!"
                    email_body += template_edit_html(row,membership_payment_request_template)
                case fmpgc_classes.Option.RENEWAL_PAYMENT:
                    subject = "FMPGC Membership Renewal Invitation!"
                    email_body += template_edit_html(row,membership_invite_to_renew_template)
                case fmpgc_classes.Option.MEMBER_RENEWED:
                    subject = "FMPGC Membership - Welcome Back!"
                    email_body += template_edit_html(row,membership_renewed_template)
                case fmpgc_classes.Option.MEMBER_EXPIRING:
                    subject = "FMPGC Membership Expiring"
                    email_body += template_edit_html(row,membership_expiring_template)
                case fmpgc_classes.Option.ADD_NEW_MEMBER:
                    subject = "Welcome to FMPGC!"
                    email_body += template_edit_html(row,membership_add_new_member_template)
                case fmpgc_classes.Option.ADD_NEW_MEMBER_EASYTEAM:
                    subject = "Welcome to FMPGC!"
                    email_body += template_edit_html(row,membership_add_new_member_easyteam_invite_template)
                case fmpgc_classes.Option.MEMBER_EXPIRED:
                    subject = "FMPGC Membership Expired - Sorry to see you go!"
                    email_body += template_edit_html(row,membership_expired_template)
                case fmpgc_classes.Option.TAILORED_TEMPLATE:
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
                    #print(f"Processing:{index} name:{name} to:{emailAddress} bcc:{bcc}")
                    print(f"Template: {broadcast_template}")
                    if onlyOnceTemplate == False:
                        subject = input('Enter Subject -> ')
                        attachment = input('Enter Attachment (blank for none) -> ')                        
                    onlyOnceTemplate = True
                    if subject == "" :
                        action = False
                        print("No subject entered, skipping email")
                    else :
                        email_body += template_edit_html(row,str(tailored_template))
                        #print(f"email body {email_body}")
            if action:
                #print(f"Sending email to:{name} to:{emailAddress} bcc:{bcc}")
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