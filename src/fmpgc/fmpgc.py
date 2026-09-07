# Imports
import argparse
import base64
from datetime import datetime
import os
import pandas as pd
import sys
from zoneinfo import ZoneInfo
from pathlib import Path
import jon_bulman_utilities

def main():
    # This ensures every time the script starts, it prints a clear timestamp
    todays_date = datetime.now(tz=ZoneInfo("Europe/London"))
    print(f"\n--- SCRIPTS STARTING: {todays_date} ---\n")

    jon_bulman_utilities.setup_environment()

    parser = argparse.ArgumentParser(description="FMPGC Email Script")
    parser.add_argument(
        "--config-file",
        "-c",
        help="Location of the config file",
        type=str,
        default="src/fmpgc/data/settings.json"
        )
    parser.add_argument(
        "--data-folder",
        "-d",
        help="Data folder location",
        type=str,
        default="src/fmpgc/data/"
        )
    parser.add_argument(
        "--membershipemail",
        "-m",
        help="FMPGC Membership email address",
        type=str,
        default="fmpgcmembership@gmail.com"
        )
    args = parser.parse_args()

    print(f"Config file: {args.config_file}")
    config_file = str(args.config_file)

    print(f"Data folder: {args.data_folder}")
    data_folder = str(args.data_folder)

    print(f"Membership email: {args.membershipemail}")
    membership_email = str(args.membershipemail)

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

    csv_file = data_folder+"fmpgc_members.csv"

    try:
        csvData = pd.read_csv(csv_file, encoding="cp1252")
    except Exception as e:
        print("Error reading CSV file:", e)
        sys.exit(1)

    if csvData is None:
        print("Error loading CSV data, exiting")
        sys.exit(1)
    else:
        # remove any blank rows
        csvData = csvData.dropna(how="all")

        try:
            for index, row in csvData.iterrows():
                name = row["Name"]
                emailAddress = row["Email"]
                invite_link = row["Invite Link"]
                print("CSV Loaded:", index, " name ", name, "email address", emailAddress, "invite link", invite_link)
            column_names = csvData.columns.tolist()
            print(f"The following {len(column_names)} may be used as variables in the html templates\n{column_names}\ne.g. {{{{Name}}}} will be replaced with that row/column contents")
        except Exception as e:
            print("Error processing CSV data:", e)
            print("Please ensure the CSV file has (at least) the following columns: Name, Email, Invite Link")
            sys.exit(1)

    try:
        htmlfile = Path(str(data_folder)) / Path("membership_new_template.html")
        membership_new_template_html = load_html_template(htmlfile)
        htmlfile = Path(str(data_folder)) / Path("membership_expiring_template.html")
        membership_expiring_template = load_html_template(htmlfile)
        htmlfile = Path(str(data_folder)) / Path("membership_expired_template.html")
        membership_expired_template = load_html_template(htmlfile)
        htmlfile = Path(str(data_folder)) / Path("membership_renewed_template.html")
        membership_renewed_template = load_html_template(htmlfile) 
    except Exception as e:
        print("Error reading HTML file:", e)
        sys.exit(1)

    #print(html)
    #input()
    print('------------- ')

    emailCC = False
    option = input('EmailCC? (non-blank is yes) -> ')
    if option != "" :
        emailCC = True

    cc = None
    if emailCC:
        cc = membership_email

    emailBCC = False
    option = input('Email as BCC (non-blank is yes)? -> ')
    if option != "" :
        emailBCC = True

    print('Options: \n'+'------------- \n'+
        '1. Add new member\n'
        '2. Member expiring\n'
        '3. Member expired\n'
        '4. Member renewal\n'
        '5. Tailored Template\n'
        )
    print('------------- ')

    onceOnly = False
    invite_link = ""
    while ( option := input('Please select required option? >> ')) in ['0', '1', '2', '3', '4','5']:
        if option == '0':
            print("Exiting")
            break
        int_Option = int(option)

        if onceOnly == False:
            onceOnly = True
            # Ask for the invite link
            invite_link = input('Enter the EasyTeam invite link -> ')

        for index, row in csvData.iterrows():
            name = row["Name"]
            emailAddress = row["Email"]
            row["Invite Link"] = invite_link
            print(f"Processing:{index} name:{name} to:{emailAddress} cc:{emailCC} bcc:{emailBCC}")
            #print(index, name, invite_link,row["Invite Link"])
            #input('Press Enter to continue...')   
            if emailCC :
                cc = membership_email
            if emailBCC :
                bcc = emailAddress
                emailAddress = None
            else :
                bcc = None
            email_body=""
            subject = ""

            action=True
            match int_Option:
                case 1:
                    subject = "Welcome to FMPGC!"
                    email_body += template_edit_html(row,membership_new_template_html)
                case 2:
                    subject = "FMPGC Membership Expiring"
                    email_body += template_edit_html(row,membership_expiring_template)
                case 3:
                    subject = "FMPGC Membership Expired - Sorry to see you go!"
                    email_body += template_edit_html(row,membership_expired_template)
                case 4:
                    subject = "FMPGC Membership Renewal - Welcome Back!"
                    email_body += template_edit_html(row,membership_renewed_template)
                case 5:
                    mbh = "membership_broadcast.html"
                    tmpl = input('Enter template name (defaults to membership_broadcast.html)-> ')
                    if tmpl == "" :
                        tmpl = mbh

                    htmlfile = Path(str(data_folder)) / Path(tmpl)
                    tailored_template = load_html_template(htmlfile)
                    subject = input('Enter Subject -> ')
                    if subject == "" :
                        action = False
                    else :
                        email_body += template_edit_html(row,str(tailored_template))
                        #print(f"email body {email_body}")
            if action:
                jon_bulman_utilities.Email_Me(credentials, token_file, emailAddress, subject, email_body,cc, bcc)

def email_header(image_src):
    body = (
        f"{image_src}<br><br>"
    )
    return body

def Load_image_as_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return ""

def load_html_template(template_path):
    try:
        html = template_path.read_text(encoding="utf-8")
        return html
    except Exception as e:
        print(f"Error loading HTML template {template_path}: {e}")
        return ""

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