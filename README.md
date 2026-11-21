# Membership Communication & Administration System

A Python-based email automation tool for managing membership communications for Flushing & Mylor Pilot Gig Club (FMPGC).

The application reads member information from a CSV file, merges member-specific data into HTML email templates, and sends personalised emails using the Gmail API. It supports common membership administration activities such as new member invitations, renewal reminders, payment requests, membership expiry notifications, and customised bulk communications.

---

## Features

### Membership Communications

- Invite prospective members to join
- Request membership payments
- Send membership renewal invitations
- Confirm membership renewals
- Notify members of upcoming membership expiry
- Notify members of expired memberships

### IT Administration

- Welcome newly added members
- Send EasyTeam invitation emails
- Manage member onboarding communications
- Notify expired members of account changes

### Personalisation

Email templates support variable substitution using any column from the membership CSV file. The variable name is defined in the header on row one for each column.

For example:

...
<p>Hello {{Name}},</p>
<p>Your membership email is {{Email}}.</p>
...

All placeholders are automatically replaced with values from the corresponding member record.

---

## Requirements

- Python 3.10 or later
- Gmail API credentials
- Google OAuth token files
- Member data in CSV format (fmpgc_members.csv)

---

## Installation

### Clone the Repository

git clone https://github.com/JonBulman/fmpgc.git
cd fmpgc

### Create a Virtual Environment

python -m venv .venv
source .venv/bin/activate

### Install Dependencies

pip install -r requirements.txt

or

pip install .

---

## Project Structure

.
├── data
│   ├── fmpgc_members.csv
│   ├── membership_add_new_member_easyteam_invite_template.html
│   ├── membership_add_new_member_template.html
│   ├── membership_broadcast.html
│   ├── membership_expired_template.html
│   ├── membership_expiring_template.html
│   ├── membership_invite_to_join_template.html
│   ├── membership_invite_to_renew_template.html
│   ├── membership_payment_request_template.html
│   ├── membership_renewed_template.html
│   └── settings.json
│
├── src
│   └── fmpgc_package
│       ├── __init__.py
│       ├── config_utils.py
│       ├── email_utils.py
│       └── fmpgc.py
│
├── pyproject.toml
├── requirements.txt
├── MANIFEST.in
└── README.md

---

## Configuration

The application loads its configuration from:

data/settings.json

Example:
{
    "GOOGLE_FMPGC_IT_CREDENTIALS": "credentials_it.json",
    "GOOGLE_FMPGC_IT_TOKEN": "token_it.json",
    "GOOGLE_FMPGC_MEMBERSHIP_CREDENTIALS": "credentials_membership.json",
    "GOOGLE_FMPGC_MEMBERSHIP_TOKEN": "token_membership.json",
    "FMPGC_IT_EMAIL": "it@fmpgc.org",
    "FMPGC_MEMBERSHIP_EMAIL": "membership@fmpgc.org",
    "FMPGC_BCC_EMAILS": "committee@fmpgc.org"
}

### Required Configuration Variables

| Setting | Description |
|----------|------------|
| GOOGLE_FMPGC_IT_CREDENTIALS | Gmail API credentials for the IT account |
| GOOGLE_FMPGC_IT_TOKEN | OAuth token for the IT account |
| GOOGLE_FMPGC_MEMBERSHIP_CREDENTIALS | Gmail API credentials for the Membership account |
| GOOGLE_FMPGC_MEMBERSHIP_TOKEN | OAuth token for the Membership account |
| FMPGC_IT_EMAIL | IT sender email address |
| FMPGC_MEMBERSHIP_EMAIL | Membership sender email address |
| FMPGC_BCC_EMAILS | Committee BCC recipients |

---

## Membership Data

The application requires a CSV file containing member information.

### Required Columns

| Column      |
|-------------|
| Name        |
| Email       |

Additional columns may be added and used within templates.

Example:

| Name     | Email            | 
|----------|------------------|
| Jane Doe | jane@example.com |

Any column can be referenced within templates:

{{Name}}
{{Email}}
...

---

## Running the Application

### Direct Execution

python src/fmpgc_package/fmpgc.py

### Installed Package

fmpgc

---

## Command Line Arguments

| Argument          | Short | Description              | Default              |
|-------------------|-------|--------------------------|----------------------|
| --data-folder     | -d    | Location of data files   | data/.               |
| --config-file     | -c    | Configuration file       | data/settings.json   |
| --membershipemail | -m    | Membership email address | membership@fmpgc.org |

Example:

python fmpgc.py \
    --data-folder data/ \
    --config-file data/settings.json \
    --membershipemail membership@fmpgc.org

---

## Menu Options

When launched, the application presents the following menu:

### Membership Functions

| Option | Description                   |
|--------|-------------------------------|
| 1      | New Member Invite             |
| 2      | Membership Payment Request    |
| 3      | Membership Renewal Invitation |
| 4      | Member Renewed                |
| 5      | Member Expiring               |

### IT Functions

| Option | Description                      |
|--------|----------------------------------|
| 6      | Add New Member                   |
| 7      | Add New Member (EasyTeam Invite) |
| 8      | Member Expired                   |

### Custom Functions

| Option | Description                 |
|--------|-----------------------------|
| 9      | Tailored Template Broadcast |

### System

| Option | Description |
|--------|-------------|
| 0      | Exit        |

---

## Email Templates

The following templates are included:

| Template | Purpose |
|-----------|----------|
| membership_invite_to_join_template.html | Invite a prospective member to join |
| membership_payment_request_template.html | Request membership payment |
| membership_invite_to_renew_template.html | Renewal invitation |
| membership_renewed_template.html | Confirmation of renewal |
| membership_expiring_template.html | Membership expiring notification |
| membership_expired_template.html | Membership expired notification |
| membership_add_new_member_template.html | Welcome email |
| membership_add_new_member_easyteam_invite_template.html | EasyTeam invitation |
| membership_broadcast.html | General-purpose broadcast |

---

## Broadcast Emails

The **Tailored Template** option provides flexible bulk mail functionality:

### Features

- Select any HTML template
- Specify a custom email subject
- Attach optional files
- Personalise content per recipient
- Send bulk communications

### Typical Use Cases

- AGM notifications
- Club newsletters
- Safety notices
- Event announcements
- Membership updates
- Training communications

---

## Email Delivery Options

The application supports:

### Direct Delivery

Emails are sent directly to each recipient.

### BCC Delivery

Recipients are added as BCC recipients, preventing exposure of email addresses to other members.

This mode is particularly useful for:

- Newsletters
- Club announcements
- Bulk communications

---

## Logging

All email activity is recorded in JSON Lines format.

Log file:

fmpgc_logs.jsonl

Example entry:

{
    "timestamp": "2026-11-21T12:00:00Z",
    "logger_name": "fmpgc",
    "level": "INFO",
    "to": "user@example.com",
    "action": "MEMBER_RENEWED",
    "result": "Success",
    "message": "from:membership@fmpgc.org"
}

### Logged Information

- Timestamp
- Recipient
- Action performed
- Send result
- Sending account
- CC information
- BCC information

---

## Gmail API Protection

To reduce the risk of hitting Gmail API rate limits, the application automatically pauses periodically:

if count % 60 == 0:
    time.sleep(60)

After every 60 emails, the application pauses for 60 seconds before continuing.

---

## Security

Never commit the following files to source control:

- Gmail API credentials
- OAuth token files
- Production member data
- Real membership exports
- Sensitive settings files

---

## Future Enhancements

Potential future improvements include:

- Scheduled mailings
- GUI interface
- Membership expiry reporting
- CSV validation tools
- Email preview mode
- Dry-run testing mode
- Enhanced quota management
- Audit reporting dashboard

---

## Licence

Internal use for Flushing & Mylor Pilot Gig Club.

---

## Author

**Jon Bulman**

Flushing & Mylor Pilot Gig Club (FMPGC) Membership Communication & Administration System.