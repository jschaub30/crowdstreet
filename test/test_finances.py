"""
Unit tests
"""
import logging
from datetime import date
import pytest

from cstreet.finances import Portfolio

LOG_LEVEL = logging.DEBUG
logging.basicConfig(format="%(levelname)s:%(message)s", level=LOG_LEVEL)


def test_init():
    """
    Initialize a Portfolio with capital contribution report
    """
    with pytest.raises(Exception):
        init_fn = "test/data/distributions.tsv"
        portfolio = Portfolio(init_fn)

    init_fn = "test/data/contributions.tsv"
    portfolio = Portfolio(init_fn)
    for txn in portfolio.transactions():
        print(txn)

    assert len(portfolio.sponsors) == 2
    assert len(portfolio.offerings) == 2
    assert len(portfolio.transactions()) == 5


def test_capital_balance():
    """
    Test capital balance with various filters
    """
    init_fn = "test/data/contributions.tsv"
    portfolio = Portfolio(init_fn)

    assert portfolio.capital_balance() == -26500
    assert portfolio.capital_balance(investing_entity="Alice") == -21000
    assert portfolio.capital_balance(investing_entity="Bob") == 0
    assert portfolio.capital_balance(investing_entity="Alice and Bob") == -5500
    assert portfolio.capital_balance(sponsor="ABC Holdings") == -16500
    assert portfolio.capital_balance(offering="Apartment ABC") == -16500


def test_date_filtering():
    """
    Test start and end date filtering
    """
    init_fn = "test/data/contributions.tsv"
    portfolio = Portfolio(init_fn)
    start = date(2023, 1, 1)
    assert len(portfolio.transactions(start_date=start)) == 1
    end = date(2022, 1, 31)
    assert len(portfolio.transactions(end_date=end)) == 2


def test_distributions():
    """
    Add distributions from distribution report
    """
    init_fn = "test/data/contributions.tsv"
    portfolio = Portfolio(init_fn)

    with pytest.raises(Exception):
        portfolio.read_distributions(init_fn)

    dist_fn = "test/data/distributions.tsv"

    sponsor = portfolio.sponsors.pop()
    with pytest.raises(Exception):
        portfolio.read_distributions(dist_fn)
    portfolio.sponsors.add(sponsor)

    offering = portfolio.offerings.pop()
    with pytest.raises(Exception):
        portfolio.read_distributions(dist_fn)
    portfolio.offerings.add(offering)

    portfolio.read_distributions(dist_fn)

    print(portfolio.transactions())
    print(len(portfolio.transactions()))
    assert len(portfolio.transactions()) == 10
    print(portfolio.capital_balance())
    assert portfolio.capital_balance() == -26100


def test_summary():
    """
    Test save summary with options
    """
    init_fn = "test/data/contributions.tsv"
    portfolio = Portfolio(init_fn)
    dist_fn = "test/data/distributions.tsv"
    portfolio.read_distributions(dist_fn)

    sum_fn = "test/data/summary.tsv"
    n1 = portfolio.save_summary(sum_fn, verbose=0)
    n2 = portfolio.save_summary(sum_fn, verbose=1)
    assert n2 > n1
    n3 = portfolio.save_summary(sum_fn, verbose=2)
    assert n3 > n2

    start_date = date(2022, 1, 1)
    end_date = date(2022, 11, 1)
    n4 = portfolio.save_summary(sum_fn, start_date=start_date, end_date=end_date)
    assert n4 == 4


def test_transactions():
    """
    Test save summary with options
    """
    init_fn = "test/data/contributions.tsv"
    portfolio = Portfolio(init_fn)
    dist_fn = "test/data/distributions.tsv"
    portfolio.read_distributions(dist_fn)
    for idx, txn in enumerate(portfolio.transactions()):
        if idx == 0:
            print(txn.headers())
        print(txn.to_tsv())


def test_capital_calls():
    """Test capital committed vs capital contributed"""
    init_fn = "test/data/contributions.tsv"
    portfolio = Portfolio(init_fn)
    committed = portfolio.capital_committed(
        investing_entity="Alice", sponsor="ABC Holdings"
    )
    contributed = portfolio.capital_contributed(
        investing_entity="Alice", sponsor="ABC Holdings"
    )

    assert contributed - committed == 1000


if __name__ == "__main__":  # pragma: no cover
    test_init()
    test_capital_balance()
    test_date_filtering()
    test_distributions()
    test_summary()
    test_transactions()
    test_capital_calls()
