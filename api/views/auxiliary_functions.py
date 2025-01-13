from django.db.models.fields.related import ManyToManyRel, OneToOneField
from django.conf import settings
from git import Repo, GitCommandError


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
    repo = Repo(settings.BASE_DIR)
    origin = repo.remote('origin')

    # check for changes
    diffs = [item.a_path for item in repo.index.diff(None)]

    try:
        if file_path in diffs:
            repo.index.add([file_path])
            repo.index.commit(commit_message)
            origin.push(refspec=f'{branch_name}:{branch_name}')

        else:
            # No changes in the specified file, nothing to push
            print(f"No changes detected in {file_path}.")
            return False

    except GitCommandError as e:
        # Handle Git-related errors (e.g., remote repository issues)
        print(f"Git command error: {e}")
        return False
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An error occurred: {e}")
        return False
