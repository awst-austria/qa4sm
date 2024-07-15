import os
from django.core.management.base import BaseCommand

from django.conf import settings
from validator.models import User
from django.urls import reverse


class Command(BaseCommand):
    help = "Generates an auto cleanup script which is then run as a cronjob to remove outdated and not published nor " \
           "archived validations."

    def add_arguments(self, parser):
        parser.add_argument('-p', '--path', type=str, help='Path prefix', )

    def handle(self, *args, **options):
        file_dir = options['path']
        cleanup_api_url = f'{settings.SITE_URL}{reverse("Run Auto Cleanup")}'
        try:
            authentication_token = User.objects.get(username='admin').auth_token
        except:
            try:
                authentication_token = User.objects.filter(is_staff=True).filter(
                    auth_token__isnull=False).first().auth_token
            except AttributeError:
                self.stdout.write(self.style.ERROR('No user with admin credentials and token assigned found.'))
                return

        script_filename = 'run_autocleanup_script.sh'
        script_content = f"""#!/bin/bash 
        curl -X POST {cleanup_api_url} -H "Authorization: Token {authentication_token.key}"
        """

        os.makedirs(file_dir, exist_ok=True)
        full_script_path = os.path.join(file_dir, script_filename)

        if not os.path.isfile(full_script_path) or authentication_token.created.timestamp() > os.stat(
                full_script_path).st_ctime:
            self.stdout.write(self.style.SUCCESS(f"Creating {script_filename} with the necessary content."))
            with open(full_script_path, 'w') as script_file:
                script_file.write(script_content)

            # Make the script executable
            os.chmod(full_script_path, 0o755)
        else:
            self.stdout.write(self.style.SUCCESS(f"{script_filename} already exists. No changes made."))

