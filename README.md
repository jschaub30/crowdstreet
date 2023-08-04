# Crowdstreet

Read and analyze [Crowdstreet](https://www.crowdstreet.com/) reports.

The data generated by this code (see this [example](test/data/summary.tsv))
is similar to the Crowdstreet "Portfolio Summary" reports with some enhancements:
- Generate CSV or TSV formats instead of PDF
- filter by start-date or end-date (e.g. 2022 tax year)

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
1. Download the "Capital Contribution" CSV report (see [example](test/data/contributions.tsv))
2. Download the "Distributions" CSV report (see [example](test/data/distributions.tsv))


## Example usage
Read CSV data and generate summary files to import into a spreadsheet for 
viewing/further analysis.
```python
from cstreet.finances import Portfolio

portfolio = Portfolio("path_to_capital_contributions.csv")
portfolio.read_distributions("path_to_distributions.csv")
portfolio.save_summary("/tmp/summary_all.tsv", verbose=0)
portfolio.save_summary("/tmp/summary_by_entity.tsv", verbose=1)
portfolio.save_summary("/tmp/summary_by_offering.tsv")  # same as verbose=2 (default)
portfolio.save_summary("/tmp/summary_by_offering.csv", delimiter=",")  # CSV
```

### Filtering by date
```python
from datetime import date
start_date = date(2022, 1, 1)
end_date = date(2022, 12, 31)
portfolio.save_summary("/tmp/summary_by_offering_2022.tsv", start_date=start_date, end_date=end_date)
```

### Analyzing individual transactions
What was the return on capital for each offering in 2022?
```python
for offering in portfolio.offerings:
    txns = portfolio.transactions(offering=offering, start_date=start_date, end_date=end_date)

    if not txns:
        continue

    ronc = 0  # return on capital

    for txn in txns:
        if txn.transaction_type == "Distribution":
            ronc += txn.return_on_capital

    ronc = round(ronc, 2)
    print(
        f"Total return on capital from offering={offering!r} " + 
        f"between {start_date} and {end_date} was ${ronc}"
    )
```

