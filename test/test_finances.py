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
    assert len(portfolio.sponsors) == 2
    assert len(portfolio.offerings) == 2

    assert portfolio.capital_balance() == 21000
    assert portfolio.capital_balance(sponsor="ABC Holdings") == 11000
    assert portfolio.capital_balance(offering="Apartment ABC") == 11000

    assert len(portfolio.transactions()) == 3
    end = date(2022, 1, 31)
    assert len(portfolio.transactions(end_date=end)) == 2
    start = date(2022, 1, 31)
    assert len(portfolio.transactions(start_date=start)) == 1


def test_distributions():
    """
    Add distributions from distribution report
    """
    init_fn = "test/data/contributions.tsv"
    portfolio = Portfolio(init_fn)

    with pytest.raises(Exception):
        portfolio.add_distributions(init_fn)

    dist_fn = "test/data/distributions.tsv"
    portfolio.add_distributions(dist_fn)

    assert len(portfolio.transactions()) == 6
    assert portfolio.capital_balance() == 21000 - 400


if __name__ == "__main__":  # pragma: no cover
    test_init()
    test_distributions()
