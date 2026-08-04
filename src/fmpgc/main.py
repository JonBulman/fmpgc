# Imports
import argparse
import base64
from dataclasses import dataclass
from datetime import datetime
import os
#from pydoc import html
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
        help="Path to the config file (default: settings.json)",
        type=str,
        default="src/fmpgc/data/settings.json"
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

    data_folder = jon_bulman_utilities.Get_Variable("FMPGC_DATA_FOLDER",config,0)
    csv_file = jon_bulman_utilities.Get_Variable("FMPGC_CSV_FILE",config,0)
    membership_email = jon_bulman_utilities.Get_Variable("FMPGC_MEMBERSHIP_EMAIL",config,0)
    it_email = jon_bulman_utilities.Get_Variable("FMPGC_IT_EMAIL",config,0)
    website = jon_bulman_utilities.Get_Variable("FMPGC_WEBSITE",config,0)
    invite_link = jon_bulman_utilities.Get_Variable("FMPGC_INVITE_LINK",config,0)
    members_area = jon_bulman_utilities.Get_Variable("FMPGC_MEMBERS_AREA",config,0)
    shed_code = jon_bulman_utilities.Get_Variable("FMPGC_SHED_CODE",config,0)
    group_email = jon_bulman_utilities.Get_Variable("FMPGC_GROUP_EMAIL",config,0)
    whatsapp_group_link = jon_bulman_utilities.Get_Variable("FMPGC_WHATSAPP_GROUP_LINK",config,0)
    easyTeam_apple=jon_bulman_utilities.Get_Variable("FMPGC_EASYTEAM_APPLE",config,0)
    easyTeam_android=jon_bulman_utilities.Get_Variable("FMPGC_EASYTEAM_ANDROID",config,0)
    membership_renewal_link = jon_bulman_utilities.Get_Variable("FMPGC_MEMBERSHIP_RENEWAL_LINK",config,0)
    image_name = jon_bulman_utilities.Get_Variable("FMPGC_IMAGE",config,0)

    template_data = FMPGCTemplateData(
        name="Jon",
        invite_link=f"{invite_link}",
        shed_code=f"{shed_code}",
        group_email=f"{group_email}",
        website=f"{website}",
        members_area=f"{members_area}",
        it_email=f"{it_email}",
        membership_email=f"{membership_email}",
        whatsapp_group_link=f"{whatsapp_group_link}",
        membership_renewal_link=f"{membership_renewal_link}",
        easyteam_apple=f"{easyTeam_apple}",
        easyteam_android=f"{easyTeam_android}"
    )

    # TODO This will not be needed if template works correctly, but for now we will load the image and convert to base64 to embed in email
    logo = image_src = imgfile = ""
    if image_name:
        imgfile = Path(str(data_folder)) / Path(str(image_name))
        print(f"img {imgfile}") 
        logo = Load_image_as_base64(imgfile)
    if logo != "":
       image_src = (
                f"<div style='text-align:center;'>"
                f"<img src=\"{logo}\" alt='Flushing & Mylor Pilot Gig Club' />"
                f"</div>"
            )
    try:
        csvfile = Path(str(data_folder)) / Path(str(csv_file))
        print(f"csv {csvfile}") 
        csvData = pd.read_csv(str(csvfile))
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

    try:
        htmlfile = Path(str(data_folder)) / Path("new_member_template.html")
        new_member_template_html = load_html_template(htmlfile)
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
    option = input('EmailCC? (1=True,0=False) -> ')
    if option == "" :
        option=0
    if int(option) == 1 :
        emailCC = True

    cc = None
    if emailCC:
        cc = membership_email

    print('Options: \n'+'------------- \n'+
        '1. Add new member\n'
        '2. Member expiring\n'
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
            template_data.name = name
            #print("Processing:",index," name ",name,"email address",emailAddress)
            email_body = email_header(image_src)
            subject = ""

            match int_Option:
                case 1:
                    subject = "Welcome to FMPGC!"
                    email_body += template_edit_html(template_data,new_member_template_html)
                case 2:
                    subject = "FMPGC Membership Expiring"
                    email_body += template_edit_html(template_data,membership_expiring_template)
                case 3:
                    subject = "FMPGC Membership Expired - Sorry to see you go!"
                    email_body += template_edit_html(template_data,membership_expired_template)
                case 4:
                    subject = "FMPGC Membership Renewal - Welcome Back!"
                    email_body += template_edit_html(template_data,membership_renewed_template)
    
            jon_bulman_utilities.Email_Me(credentials, token_file, emailAddress, subject, email_body,cc)

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

@dataclass
class FMPGCTemplateData:
    name: str
    invite_link: str
    shed_code: str
    group_email: str
    website: str
    members_area: str
    it_email: str
    membership_email: str
    whatsapp_group_link: str
    membership_renewal_link: str
    easyteam_apple: str
    easyteam_android: str


def template_edit_html(data: FMPGCTemplateData, inputhtml: str) -> str:
    body = inputhtml

    # Loop through dataclass fields and replace {{field}} in the HTML
    for field, value in data.__dict__.items():
        #print(f"field:{field}")
        body = body.replace(f"{{{{{field}}}}}", str(value))

    return body


if __name__ == "__main__":
    main()