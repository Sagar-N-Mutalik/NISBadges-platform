from django.core.management.base import BaseCommand
from core_accounts.models import CoreUser

USERS_DATA = [
    {"full_name": "AADYA SHARMA", "email": "aadyasharma@ieee.org", "password": "100640650", "role": "core_member"},
    {"full_name": "Aashish Vatwani", "email": "aashishvatwani01@ieee.org", "password": "99694127", "role": "core_member"},
    {"full_name": "Abhay Hegde", "email": "abhayhegde@ieee.org", "password": "99694320", "role": "co_admin"},
    {"full_name": "Amol S", "email": "amolakki90@gmail.com", "password": "101159483", "role": "core_member"},
    {"full_name": "K Anantha Krishna Rao", "email": "ananthakrishnakrao@ieee.org", "password": "99694255", "role": "core_member"},
    {"full_name": "Mohammed Mansooruddin", "email": "mohammedmansoor2908@gmail.com", "password": "101144197", "role": "core_member"},
    {"full_name": "Panchami Urs S", "email": "panchamiurs25@ieee.org", "password": "101128727", "role": "core_member"},
    {"full_name": "Pranav A Korlahalli", "email": "pranav.ak@ieee.org", "password": "100651733", "role": "core_member"},
    {"full_name": "Prerika P", "email": "prerikap@ieee.org", "password": "99708830", "role": "core_member"},
    {"full_name": "Priyanka Pramod Daivagna", "email": "priyanka_daivagna@ieee.org", "password": "101259576", "role": "core_member"},
    {"full_name": "Rachit Ravinandan Kulkarni", "email": "rachit_kulkarni@ieee.org", "password": "101125297", "role": "core_member"},
    {"full_name": "Rahul K", "email": "rahulkaratha@ieee.org", "password": "101177969", "role": "core_member"},
    {"full_name": "Sagar Kumar Singh", "email": "sagarks@ieee.org", "password": "99690873", "role": "co_admin"},
    {"full_name": "Sagar N Mutalik", "email": "sagarnmutalik6@gmail.com", "password": "100678061", "role": "main_admin"},
    {"full_name": "Sakaleshwar C Hubli", "email": "Sakaleshhubli@ieee.org", "password": "99702057", "role": "core_member"},
    {"full_name": "Sanjana S Shetty", "email": "sanjanasshetty@ieee.org", "password": "100815121", "role": "core_member"},
    {"full_name": "Shresth Juptimath", "email": "shresht@gmail.com", "password": "100676913", "role": "core_member"},
    {"full_name": "Shreya P V", "email": "shreyapv2105@ieee.org", "password": "101116953", "role": "core_member"},
    {"full_name": "Suma Acharya", "email": "suma@gmail.com", "password": "100478621", "role": "core_member"},
    {"full_name": "Yogesh S", "email": "yogesh.s@ieee.org", "password": "100677143", "role": "core_member"},
    {"full_name": "Nikitha H S", "email": "nikithahs30@gmail.com", "password": "102021437", "role": "core_member"}
]

class Command(BaseCommand):
    help = 'Pre-seed the database with core team members'

    def handle(self, *args, **kwargs):
        for user_data in USERS_DATA:
            email = user_data["email"]
            full_name = user_data["full_name"]
            password = user_data["password"]
            role = user_data["role"]
            is_staff = role in ["main_admin", "co_admin"]

            try:
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
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated existing user: {email}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Skipped existing user: {email}'))

            except CoreUser.DoesNotExist:
                user = CoreUser(
                    email=email,
                    full_name=full_name,
                    role=role,
                    is_staff=is_staff
                )
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully created new user: {email}'))

        self.stdout.write(self.style.SUCCESS('Successfully completed seeding the database with predefined users.'))
