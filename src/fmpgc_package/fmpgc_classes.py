
from enum import IntEnum

class Option(IntEnum):
    NEW_MEMBER_INVITE = 0
    JOINING_MEMBER_PAYMENT = 1
    RENEWAL_PAYMENT = 2
    MEMBER_RENEWED = 3
    MEMBER_EXPIRING = 4
    ADD_NEW_MEMBER = 5
    ADD_NEW_MEMBER_EASYTEAM = 6
    MEMBER_EXPIRED = 7
    TAILORED_TEMPLATE = 8
    EXIT = 9

OPTION_DEFINITIONS = [
    ("New Member invite to join (personal details request)", Option.NEW_MEMBER_INVITE, "FMPGC Invitation to Join!", "membership_invite_to_join_template.html"),
    ("Joining Member Payment Request", Option.JOINING_MEMBER_PAYMENT, "FMPGC Membership Payment Request!", "membership_payment_request_template.html"),
    ("Renewal Payment Invitation", Option.RENEWAL_PAYMENT, "FMPGC Membership Renewal Invitation!", "membership_invite_to_renew_template.html"),
    ("Member Renewed (Welcome Back)", Option.MEMBER_RENEWED, "FMPGC Membership - Welcome Back!", "membership_renewed_template.html"),
    ("Member Expiring", Option.MEMBER_EXPIRING, "FMPGC Membership Expiring", "membership_expiring_template.html"),
    ("Add New Member", Option.ADD_NEW_MEMBER, "Welcome to FMPGC!", "membership_add_new_member_template.html"),
    ("Add New Member (EasyTeam Invite)", Option.ADD_NEW_MEMBER_EASYTEAM, "Welcome to FMPGC!", "membership_add_new_member_easyteam_invite_template.html"),
    ("Member Expired", Option.MEMBER_EXPIRED, "FMPGC Membership Expired - Sorry to see you go!", "membership_expired_template.html"),
    ("Tailored / Broadcast Template", Option.TAILORED_TEMPLATE, "Membership Broadcast","membership_broadcast.html"),
    ("Exit", Option.EXIT, "Exit the program", None)
]
class IT_OPTIONS(IntEnum):
    ADD_NEW_MEMBER = 5
    ADD_NEW_MEMBER_EASYTEAM = 6
    MEMBER_EXPIRED = 7
    TAILORED_TEMPLATE = 8

class MEMBERSHIP_OPTIONS(IntEnum):
    NEW_MEMBER_INVITE = 0
    JOINING_MEMBER_PAYMENT = 1
    RENEWAL_PAYMENT = 2
    MEMBER_RENEWED = 3
    MEMBER_EXPIRING = 4

class CC_MEMBERSHIP_OPTIONS(IntEnum):
    ADD_NEW_MEMBER = 5
    ADD_NEW_MEMBER_EASYTEAM = 6
    MEMBER_EXPIRED = 7
    


