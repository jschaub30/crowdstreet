# Crowdstreet

Read and analyze [Crowdstreet](https://www.crowdstreet.com/) reports.

## Prerequisites

- python
- pyenv (optional)
- make (optional)

## Setup using pyenv

```bash
pyenv virtualenv 3.8.11 crowdstreet
pyenv activate crowdstreet
pip install -r requirements-tests.txt
```
then
```bash
make test
```
or
```bash
pytest
```

## Crowdstreet setup
1. Download the "Capital Contribution" CSV report
2. Download the "Distributions" CSV report
