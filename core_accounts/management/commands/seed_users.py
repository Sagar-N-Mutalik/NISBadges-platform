Here is the complete code for your `seed_users.py` file with all 21 team members from your original seed file, safely stripped of their hardcoded passwords:

```python
from django.core.management.base import BaseCommand
from core_accounts.models import CoreUser

# Notice: Passwords have been completely removed from this list
USERS_DATA = [
    {"full_name": "AADYA SHARMA", "email": "aadyasharma@ieee.org", "role": "core_member"},
    {"full_name": "Aashish Vatwani", "email": "aashishvatwani01@ieee.org", "role": "core_member"},
    {"full_name": "Abhay Hegde", "email": "abhayhegde@ieee.org", "role": "co_admin"},
    {"full_name": "Amol S", "email": "amolakki90@gmail.com", "role": "core_member"},
    {"full_name": "K Anantha Krishna Rao", "email": "ananthakrishnakrao@ieee.org", "role": "core_member"},
    {"full_name": "Mohammed Mansooruddin", "email": "mohammedmansoor2908@gmail.com", "role": "core_member"},
    {"full_name": "Panchami Urs S", "email": "panchamiurs25@ieee.org", "role": "core_member"},
    {"full_name": "Pranav A Korlahalli", "email": "pranav.ak@ieee.org", "role": "core_member"},
    {"full_name": "Prerika P", "email": "prerikap@ieee.org", "role": "core_member"},
    {"full_name": "Priyanka Pramod Daivagna", "email": "priyanka_daivagna@ieee.org", "role": "core_member"},
    {"full_name": "Rachit Ravinandan Kulkarni", "email": "rachit_kulkarni@ieee.org", "role": "core_member"},
    {"full_name": "Rahul K", "email": "rahulkaratha@ieee.org", "role": "core_member"},
    {"full_name": "Sagar Kumar Singh", "email": "sagarks@ieee.org", "role": "co_admin"},
    {"full_name": "Sagar N Mutalik", "email": "sagarnmutalik6@gmail.com", "role": "main_admin"},
    {"full_name": "Sakaleshwar C Hubli", "email": "Sakaleshhubli@ieee.org", "role": "core_member"},
    {"full_name": "Sanjana S Shetty", "email": "sanjanasshetty@ieee.org", "role": "core_member"},
    {"full_name": "Shresth Juptimath", "email": "shresht@gmail.com", "role": "core_member"},
    {"full_name": "Shreya P V", "email": "shreyapv2105@ieee.org", "role": "core_member"},
    {"full_name": "Suma Acharya", "email": "suma@gmail.com", "role": "core_member"},
    {"full_name": "Yogesh S", "email": "yogesh.s@ieee.org", "role": "core_member"},
    {"full_name": "Nikitha H S", "email": "nikithahs30@gmail.com", "role": "core_member"}
]

class Command(BaseCommand):
    help = 'Pre-seed the database with core team members securely'

    def handle(self, *args, **kwargs):
        for user_data in USERS_DATA:
            email = user_data["email"]
            full_name = user_data["full_name"]
            role = user_data["role"]
            is_staff = role in ["main_admin", "co_admin"]

            try:
                # Update existing users without touching their passwords
                user = CoreUser.objects.get(email=email)
                updated = False
                if user.full_name != full_name:
                    user.full_name = full_name
                    updated = True
                if user.role != role:
                    user.role = role
                    updated = True
                if user.is_staff != is_staff:
                    user.is_staff = is_staff
                    updated = True

                if updated:
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'Updated existing user: {email}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Skipped existing user: {email}'))

            except CoreUser.DoesNotExist:
                # Create new users securely
                user = CoreUser(
                    email=email,
                    full_name=full_name,
                    role=role,
                    is_staff=is_staff
                )
                # SECURE: This locks the account until an admin sets a password in the UI
                user.set_unusable_password() 
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created new user (locked): {email}'))

        self.stdout.write(self.style.SUCCESS('Successfully completed syncing users.'))
```