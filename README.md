# FMPGC Membership Communication & Administration System

A Python-based email automation tool for managing membership communications for **Flushing & Mylor Pilot Gig Club (FMPGC)**.

The application reads member details from a CSV file, merges member-specific data into HTML email templates, and sends personalised emails via the Gmail API. It supports routine membership administration—including new member invitations, payment requests, renewal reminders, onboarding emails, expiry notifications, and custom bulk broadcasts.

## Table of Contents

* [Features](#features)
* [Requirements](#requirements)
* [Installation](#installation)
* [Google OAuth & Gmail API Setup](#google-oauth--gmail-api-setup)
* [Configuration](#configuration)
* [Membership CSV Format](#membership-csv-format)
* [Usage](#usage)
  * [Running the Application](#running-the-application)
  * [Command-Line Arguments](#command-line-arguments)
  * [Menu Options](#menu-options)
  * [Email Delivery Modes](#email-delivery-modes)
  * [Tailored Broadcast Emails](#tailored-broadcast-emails)
* [Email Templates](#email-templates)
* [Logging & Rate Limiting](#logging--rate-limiting)
* [Project Structure](#project-structure)
* [Security](#security)
* [Future Enhancements](#future-enhancements)
* [Licence & Author](#licence--author)

## Features

### Membership Communications

* Invite prospective members to join
* Request membership payments
* Send membership renewal invitations
* Confirm completed renewals
* Notify members of upcoming membership expiry
* Notify members of expired memberships

### IT Administration

* Welcome newly added members
* Send EasyTeam invitation emails
* Automatically CC the membership inbox on relevant IT onboarding actions
* Manage member onboarding and account change notifications

### Template Personalisation

Email templates support dynamic variable substitution using any column header from row one of the membership CSV file:

```html
<p>Hello {{Name}},</p>
<p>Your registered membership email is {{Email}}.</p>
```

All `{{ColumnName}}` placeholders are automatically replaced with the corresponding value from each member's row.

## Requirements

* **Python 3.10 or later** (required for `match`/`case` syntax and `zoneinfo`)
* **Gmail API credentials** (OAuth 2.0 client JSON files for the IT and Membership Google accounts)
* **Google OAuth token files** (generated automatically on first sign-in)
* **Member data CSV file** (`data/fmpgc_members.csv`)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/JonBulman/fmpgc.git
cd fmpgc
```

### 2. Create and Activate a Virtual Environment

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

Install dependencies directly:

```bash
pip install -r requirements.txt
```

Or install as a package (recommended to enable the `fmpgc` CLI command):

```bash
pip install .
```

## Google OAuth & Gmail API Setup

Because the application sends emails via the Gmail API from two accounts (IT and Membership), you need OAuth 2.0 Desktop App credentials from Google Cloud Console.

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project selector in the top-left bar and choose **New Project**.
3. Give the project a recognisable name (e.g., `FMPGC Membership Mailer`) and click **Create**.
4. Make sure the newly created project is selected.

### 2. Enable the Gmail API

1. In the left navigation menu, go to **APIs & Services > Library**.
2. Search for **Gmail API**.
3. Click **Gmail API** and select **Enable**.

### 3. Configure the OAuth Consent Screen

1. Go to **Google Auth Platform** (or **APIs & Services > OAuth consent screen**).
2. Click **Get Started** (if not yet configured) and fill in the app details:
   * **App name:** `FMPGC Membership Mailer`
   * **User support email:** Your IT or Membership email address
   * **Audience:** Select **External** (unless using a Google Workspace organisation account, in which case choose **Internal**)
   * **Contact information:** Your IT admin email address
3. Under **Audience > Test users** (required while the app is in **Testing** status), click **Add users** and add both the **IT email address** and the **Membership email address**.
4. Under **Data Access** (or **Scopes**), add the Gmail API scope required for sending emails (e.g., `https://www.googleapis.com/auth/gmail.send`).
5. Save your changes.

### 4. Create OAuth 2.0 Client Credentials

1. Go to **Google Auth Platform > Clients** (or **APIs & Services > Credentials**).
2. Click **Create Client** (or **+ Create Credentials > OAuth client ID**).
3. Set **Application type** to **Desktop app**.
4. Give it a name (e.g., `FMPGC Desktop Client`) and click **Create**.
5. Click **Download JSON** to save the credentials file to your computer.

> **Tip:** Both the IT and Membership accounts can use copies of the same Desktop OAuth client JSON file (provided both email addresses are listed as test users), or you can create a separate Google Cloud project/client for each account. However, each account **must** point to its own distinct token file in `fmpgc_settings.json`.

### 5. Place Credentials and Generate OAuth Tokens

1. Rename/copy the downloaded JSON file(s) to match the paths configured in `data/fmpgc_settings.json` (for example, `credentials_it.json` and `credentials_membership.json`).
2. The first time you send an email from either the **Membership** or **IT** account, a browser window will open asking you to sign in to Google and grant permission:
   * Sign in with the **corresponding account** (IT account for IT menu options; Membership account for Membership menu options).
   * If you see a *"Google hasn't verified this app"* warning (normal for internal/testing apps), click **Advanced > Go to FMPGC Membership Mailer (unsafe)** and grant access.
3. Once authorised, the application will automatically create `token_it.json` and/or `token_membership.json` for future runs.

> **Note on Token Expiry:** While a Google OAuth app with an **External** audience remains in **Testing** mode, refresh tokens expire after **7 days**. If authentication fails with an `invalid_grant` error, delete the expired `token_*.json` file and re-run the script to re-authorise.

## Configuration

By default, the application loads its configuration from `data/fmpgc_settings.json`.

### Example `data/settings.json`

```json
{
    "FMPGC_IT_EMAIL": "fmpgc_it@gmail.com",
    "GOOGLE_FMPGC_IT_CREDENTIALS": "your it credentials file.json",
    "GOOGLE_FMPGC_IT_TOKEN": "your it token file.json",

    "FMPGC_MEMBERSHIP_EMAIL": "fmpgcmembership@gmail.com",
    "GOOGLE_FMPGC_MEMBERSHIP_CREDENTIALS": "your membership credentials file.json",
    "GOOGLE_FMPGC_MEMBERSHIP_TOKEN": "your membership token file.json",
    
    "FMPGC_BCC_EMAILS": "chair.fmpgc@gmail.com"
}
```

### Configuration Variables

| Setting | Description |
| ----- | ----- |
| `GOOGLE_FMPGC_IT_CREDENTIALS` | Path to Gmail API credentials JSON for the IT account |
| `GOOGLE_FMPGC_IT_TOKEN` | Path to OAuth token file for the IT account |
| `GOOGLE_FMPGC_MEMBERSHIP_CREDENTIALS` | Path to Gmail API credentials JSON for the Membership account |
| `GOOGLE_FMPGC_MEMBERSHIP_TOKEN` | Path to OAuth token file for the Membership account |
| `FMPGC_IT_EMAIL` | Sender email address for IT administration emails |
| `FMPGC_MEMBERSHIP_EMAIL` | Sender email address for Membership emails |
| `FMPGC_BCC_EMAILS` | Committee email address(es) BCC'd on applicable new member emails |

## Membership CSV Format

The application reads member records from `<data-folder>/fmpgc_members.csv` (or from the file specified in the command line) using `cp1252` (Windows-1252) encoding and automatically drops completely blank rows.

### Required Columns

The script requires the following column headers to be present in row 1:

| Column | Purpose |
| ----- | ----- |
| `Name` | Member's name |
| `Email` | Member's email address |
| `Invite Link` | Invitation URL (validated on startup) |
| `Membership Type` | Member category (used to determine committee BCC rules; e.g., `Concessionary (FXU)` members are excluded from committee BCCs in direct mode) |

Any additional columns added to the CSV are automatically available as `{{ColumnName}}` placeholders in your HTML templates. On startup, the script prints the full list of available template variables.

### Example CSV

```csv
Name,Email,Invite Link,Membership Type
Jane Doe,jane@example.com,https://example.com/invite/123,Adult
John Smith,john@example.com,https://example.com/invite/456,Concessionary (FXU)
```

## Usage

### Running the Application

If installed as a package:

```bash
fmpgc
```

Or run directly with Python:

```bash
python src/fmpgc_package/fmpgc.py
```

### Command-Line Arguments

| Argument            | Short  | Description | Default |
| ------------------- | ------ | ----- | ----- |
| `--data-folder`     | `-d`   | Directory containing CSV and HTML templates *(include trailing slash)* | `data/` |
| `--config-file`     | `-c`   | Path to the JSON configuration file         | `data/fmpgc_settings.json` |
| `--csv-file`        | `-csv` | Path to the people to email in a csv format | `data/fmpgc_members.csv`   |
| `--membershipemail` | `-m`   | Membership email address used for CCing on relevant IT actions   | `fmpgcmembership@gmail.com` |

**Example:**

```bash
fmpgc \
    --data-folder data/ \
    --config-file data/fmpgc_settings.json \
    --csv-file    data/fmpgc_members.csv \
    --membershipemail fmpgcmembership@gmail.com
```

### Menu Options

When launched, the application prompts for the delivery mode (Direct vs. BCC) and displays an interactive menu:

#### Membership Functions *(sent from `FMPGC_MEMBERSHIP_EMAIL`)*

| Option | Description | Default Subject |
| ----- | ----- | ----- |
| `1` | New Member Invite | `FMPGC Invitation to Join!` |
| `2` | Membership Payment Request | `FMPGC Membership Payment Request!` |
| `3` | Membership Renewal Invitation | `FMPGC Membership Renewal Invitation!` |
| `4` | Member Renewed | `FMPGC Membership - Welcome Back!` |
| `5` | Member Expiring | `FMPGC Membership Expiring` |

#### IT Functions *(sent from `FMPGC_IT_EMAIL`)*

| Option | Description | Default Subject |
| ----- | ----- | ----- |
| `6` | Add New Member | `Welcome to FMPGC!` |
| `7` | Add New Member (EasyTeam Invite) | `Welcome to FMPGC!` |
| `8` | Member Expired | `FMPGC Membership Expired - Sorry to see you go!` |

#### Custom & System Functions

| Option | Description |
| ----- | ----- |
| `9` | Tailored Template Broadcast |
| `0` | Exit |

### Email Delivery Modes

At startup, you will be prompted:

```text
Send Email as BCC to recipient? (non-blank is yes)? ->
```

* **Direct Delivery (leave blank):** Emails are addressed directly to each recipient in the `To` field. For `Add New Member` and `Add New Member (EasyTeam Invite)`, `FMPGC_BCC_EMAILS` is automatically BCC'd unless the member's `Membership Type` is `Concessionary (FXU)` or blank.
* **BCC Delivery (enter any character):** Recipients are placed in the `BCC` field rather than `To`. Ideal for newsletters, club announcements, and bulk communications.

### Tailored Broadcast Emails

Selecting option **9 (Tailored Template Broadcast)** lets you send custom bulk emails:

1. Choose any HTML template in your data folder (defaults to `membership_broadcast.html`).
2. Enter a custom email subject (leaving the subject blank skips sending).
3. Optionally specify a file path for an attachment.

Typical use cases include AGM notifications, club newsletters, safety notices, event announcements, and training updates.

## Email Templates

The following HTML templates are expected in the `data/` directory:

| Template File | Purpose |
| ----- | ----- |
| `membership_invite_to_join_template.html` | Invite a prospective member to join |
| `membership_payment_request_template.html` | Request membership payment |
| `membership_invite_to_renew_template.html` | Send a renewal invitation |
| `membership_renewed_template.html` | Confirm a completed renewal |
| `membership_expiring_template.html` | Notify of upcoming membership expiry |
| `membership_expired_template.html` | Notify of expired membership |
| `membership_add_new_member_template.html` | Welcome email for new members |
| `membership_add_new_member_easyteam_invite_template.html` | Welcome email with EasyTeam invitation |
| `membership_broadcast.html` | Default template for custom broadcasts |

## Logging & Rate Limiting

### Activity Logs

All email activity is recorded in **JSON Lines** format in `fmpgc_logs.jsonl` (alongside general application logs in `fmpgc.log`).

Example `fmpgc_logs.jsonl` entry:

```json
{
    "timestamp": "2026-11-21T12:00:00Z",
    "logger_name": "fmpgc",
    "level": "INFO",
    "to": "user@example.com",
    "action": "MEMBER_RENEWED",
    "result": "Success",
    "message": "from:membership@fmpgc.org"
}
```

Each entry captures the timestamp, recipient, action performed, delivery result, sender account, and any CC/BCC recipients.

### Gmail API Rate-Limit Protection

To avoid hitting Gmail API rate limits during large mailings, the script automatically pauses for **60 seconds after every 60 emails**:

```python
if count % 60 == 0:
    time.sleep(60)
```

## Project Structure

```text
.
├── data/
│   ├── fmpgc_members.csv
│   ├── fmpgc_settings.json
│   ├── membership_add_new_member_easyteam_invite_template.html
│   ├── membership_add_new_member_template.html
│   ├── membership_broadcast.html
│   ├── membership_expired_template.html
│   ├── membership_expiring_template.html
│   ├── membership_invite_to_join_template.html
│   ├── membership_invite_to_renew_template.html
│   ├── membership_payment_request_template.html
│   └── membership_renewed_template.html
├── src/
│   └── fmpgc_package/
│       ├── __init__.py
│       ├── config_utils.py
│       ├── email_utils.py
│       ├── fmpgc.py
│       └── fmpgc_classes.py
├── fmpgc_logs.jsonl
├── MANIFEST.in
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Security

Never commit sensitive club or authentication files to version control (ensure these are listed in `.gitignore`):

* Gmail API credentials (`credentials_*.json`)
* OAuth token files (`token_*.json`)
* Production member data (`fmpgc_members.csv`)
* Real membership exports or log files containing member emails (`fmpgc_logs.jsonl`)
* Live configuration files (`data/fmpgc_settings.json`)

## Future Enhancements

* Dry-run / preview mode before sending bulk emails
* Scheduled mailings
* GUI interface
* Membership expiry reporting
* Automated CSV validation tool
* Enhanced Gmail quota management
* Audit reporting dashboard

## Licence & Author

**Licence:** Internal use for Flushing & Mylor Pilot Gig Club (FMPGC).

**Author:** Jon Bulman