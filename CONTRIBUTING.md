# Contributing to SimplePlaygrounds

SimplePlaygrounds welcomes contributions, including:
 - Bug reports & feature suggestions
 - Bug fixes
 - Implementations of requested features
 - Corrections & additions to the documentation
 - Improvements to the tests

If you're looking for a way to contribute, try checking the currently active issues for one that needs work.
You can also ask us to join our Discord server.

## Virtual Environment

First of all, we recommend that you use a virtual environment for development.
For example, you can use the built-in venv module to create a virtual environment named venv in the current directory:

```bash
pyenv virtualenv 3.10.0 spg
```

Then, activate the virtual environment:

```bash
pyenv activate spg
```

## Development Dependencies

To install all necessary development dependencies, create a feature branch and run this command in your terminal
from inside the top level of the simple-playgrounds project directory:

```bash
pip install -e '.[dev]'
```

## Pre-commit Checks

We request that all new PRs go through pre-commit checks.
To install the pre-commit hooks, run this command in your terminal from inside the top level of the SPG directory:

```bash
pre-commit install
```

This will make sure that your PRs pass the pre-commit checks and follow standard formatting.

## How to contribute

Make a PR to the branch `develop` with your changes.

## Testing

We recommend that you implement tests for your changes.
You should verify that previous tests are still passing as well.

To run the tests, run this command in your terminal from inside the top level of the arcade directory:

```bash
pytest tests
```

# Feature requests

If you have a feature request, please open an issue on GitHub.