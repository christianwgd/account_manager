[![Django CI run test](https://github.com/christianwgd/account_manager/actions/workflows/django-test.yml/badge.svg)](https://github.com/christianwgd/account_manager/actions/workflows/django-test.yml)

# Account Manager
Manage email accounts for different tenants and domains

I'm an admin of different mail servers and now and then people call 
me to get a new password (most they move to a new hardware and don't 
remember their passwords). So every time i had to generate a new passwod 
(never give them a simple one, they will never change ;-)), write a mail 
and tell them their new passwords. Same for new users, which need to get 
all account data including some advice how to configure their email clients.

Since i was going mad about this mail traffic, i build this app to generate 
passwords and a PDF that i can mail to the users. The PDF includes all relevant 
information to access the mails with an email client.

There's one thing i'm still missing: Unfortunately no email provider will ever
provide a webservice to manage email accounts. Hints are welcome!
