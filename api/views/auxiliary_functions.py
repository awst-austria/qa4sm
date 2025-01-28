import os
import logging
from urllib.parse import urlparse, urlunparse

from django.db.models.fields.related import ManyToManyRel, OneToOneField
from django.conf import settings
from git import Repo, GitCommandError

__logger = logging.getLogger(__name__)

def get_fields_as_list(model):
    fields = []
    for field in model._meta.get_fields():
        if isinstance(field, ManyToManyRel):
            fields.append(field.related_name)
        elif not isinstance(field, OneToOneField):
            fields.append(field.name)
    for property_name in list(model._meta._property_names):
        fields.append(property_name)
    return fields


def clean_redundant_datasets(user_datasets_without_file):
    for dataset in user_datasets_without_file:
        versions = dataset.versions.all()
        variables = dataset.variables.all()
        for version in versions:
            version.delete()
        for variable in variables:
            variable.delete()

        dataset.delete()


def push_changes_to_github(file_path, commit_message, branch_name='master'):
    """
    Pushes changes to our github repository

    Args:
        file_path (str): relative (to the project) path of a file to be commited,
        commit_message (str): commit message,
        branch_name (str): Branch to push to (default: 'master'),

    Parameters
    ----------
    file_path
    commit_message
    branch_name
    """
    # our repository is initialized here

    repo_dir = os.path.join(settings.BASE_DIR, 'validator', 'fixtures')
    repo = Repo(repo_dir)
    origin = repo.remote('origin')

    parsed_url = urlparse(origin.url)
    updated_url = urlunparse(parsed_url._replace(netloc=f'{settings.GITHUB_USERNAME}:{settings.GITHUB_TOKEN}@{parsed_url.hostname}'))
    repo.git.config('remote.origin.url', updated_url)  # Update the remote URL with credentials

    # check for changes
    diffs = [item.a_path for item in repo.index.diff(None)]

    try:
        if file_path in diffs:
            repo.index.add([file_path])
            repo.index.commit(commit_message)
            origin.push(refspec=f'{branch_name}:{branch_name}')

        else:
            # No changes in the specified file, nothing to push
            __logger.debug(f"No changes detected in {file_path}.")
            return

    except GitCommandError as e:
        # Handle Git-related errors (e.g., remote repository issues)
        __logger.error(f"Git command error: {e}")
        return
    except Exception as e:
        # Handle any other unexpected errors
        __logger.error(f"An error occurred: {e}")
        return
