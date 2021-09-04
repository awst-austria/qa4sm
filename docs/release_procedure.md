# QA4SM Release procedure

Releasing a new version of QA4SM has several aspects:

- Managing the versions of dependencies
- Developing a new release
- Pushing out the new release

Updating dependency versions can be done at any time during the development but should happen before manual testing for the release.

## Dependency version management

1. Create a new environment, e.g. with the `environment/create_conda_env.sh` (if it doesn't work try with `sudo`) script or by updating single python packages in `environment/qa4sm_env.yml`.
2. Activate the new environment `conda activate new_env` (if the path has not been changed: new_env = /var/lib/qa4sm-conda).
3. Test for regressions/problems by running all integration/unit tests with `pytest -m ""` and fix all issues (in particular those coming from updated dependencies).
4. Test for regressions manually by inspecting all pages and all major functionality of the webapp.
5. Export the new_env to .yml file: `conda env export --no-builds > environment/qa4sm_env.yml`.
6. Verify that the generated environment file can be used to recreate the environment with (after deactivating other conda environments):

        conda env create -f qa4sm_env.yml -n my_environment_name

7. Add the resulting `qa4sm_env.yml` file to the git repository. If code changes were necessary because of dependency version changes, commit them together with the environment file.

Note: You can remove unwanted conda environments with:

    conda env remove -n name_of_environment

If you have access to the AWST buildserver, you can do steps 1-4 by running build job "Conda environment". Well, obviously not the fixing of issues, that you have to do yourself ;-)

## Development

0. Set up your conda environment using the *current* `qa4sm_env.yml` file. If you or another contributor updates the environment, ideally switch to the new environment soon.

        conda env create -f qa4sm_env.yml -n my_environment_name

1. Make and commit your development changes to a feature branch.
2. Perform testing (includes unit tests).
3. Create pull request to the master branch.
4. Peer review of the changes. Peer also needs to use the current `qa4sm_env.yml` environment.
5. Merge the feature branch into the master branch.

## Release

1. Perform integration testing (including the long unit tests and manual tests). Usually, manual testing should only happen after all automatic tests succeed in order to save the testers' time.
2. Update the test system to be used for testing to the current `qa4sm_env.yml` environment.

        conda env create -f qa4sm_env.yml -n my_environment_name

3. Deploy the release candidate to the test system.

4. Decide which version number to use. The format should be v(MAJOR).(MINOR).(PATCH).
    * major: Indicates a significant change in the application which may essentially mean one of the following:
        * The app is re-written
        * The app has changed significantly so much so that backward compatibility with older versions gets broken.
        * Large set of new features
        * At times, new UI can also be released as major release.
    * minor: Indicates the release of one or more newer features or major enhancements representing a set of bug fixes on previous major release. Minor releases do not break the backward compatibility of the product.
    * patch: Indicates one or more bug fixes related with one or more existing features which need to be released in between minor releases. Patch release never releases a new functionality.

    Source: <https://vitalflux.com/software-build-release-versioning-strategy/>

5. Create a release-notes.md file in the root of the repository using the template at the end of this procedure. It should contain the new version number and list new features, fixes and improvements in the new release. Add it to the repository.

6. Update the version number in `valentina/version.py`. Commit your release notes and version increase.

7. Commit your changes again and create an annotated tag using the following command:

        git tag -a v1.1.1 -m "Version 1.1.1, created YYYY-mm-dd"

8. Deploy on the ops system from the tag
9. Don't forget to set the data paths again using the `python manage.py setdatasetpaths` command.


## Release notes template

        QA4SM v(MAJOR).(MINOR).(PATCH) - Release notes ((DATE))
        =======================================================

        # New features

        1. (Feature 1)
        2. (Feature 2)
        3. (Feature 3)


        # Fixes

        1. (Fix 1)
        2. (Fix 2)
        3. (Fix 3)

        # Improvements

        1. (Improvement 1)
        2. (Improvement 2)
        3. (Improvement 3)

        # Other changes

        1. (Change 1)
        2. (Change 2)
        3. (Change 3)
