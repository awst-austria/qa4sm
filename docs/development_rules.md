## Coding Style

4 spaces instead of tabs.

## Definition Of Done

Before you say a backlog item is done, check the following list and make sure you can tick off all points:

* The software fulfills all aspects mentioned in the issue.
* The acceptance criteria are met (if they exist).
* The code is commited to version control (git).
* Unit tests are written to cover the new code; (ideally all lines, including edge cases and errors)
* Implementation doesn't break existing code, i.e. all unit tests pass.
* The package was tested by downloading it from scratch into a clean build environment and running the tests. (Use a buildserver to make your life easier!)
* Someone else has reviewed the change and verified it.
* The implementation is merged into the main branch of the main repository - e.g. via a pull request.
* Jira issue for the backlog item has been updated with the latest information (comments, status change, reassignment, etc.).
