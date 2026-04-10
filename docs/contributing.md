# Contributing

Contributions are welcome! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/bnznamco/django-structured-metaobjects.git
cd django-structured-metaobjects
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Running Tests

```bash
make test
```

This runs flake8 linting followed by pytest with coverage reporting.

## Code Style

- Follow [Django coding style](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)
- Max line length: 160 characters
- Max complexity: 20

## Commit Messages

This project uses [semantic-release](https://python-semantic-release.readthedocs.io/) for automated versioning. Please follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` — new feature (minor version bump)
- `fix:` — bug fix (patch version bump)
- `feat!:` or `BREAKING CHANGE:` — breaking change (major version bump)

## Reporting Issues

- **Bug reports**: open a GitHub issue with steps to reproduce
- **Feature requests**: open a GitHub issue describing the use case
