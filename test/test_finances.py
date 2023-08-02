"""
Unit tests
"""
import logging
import pytest

from cstreet.finances import Portfolio

LOG_LEVEL = logging.DEBUG
logging.basicConfig(format="%(levelname)s:%(message)s", level=LOG_LEVEL)


def test_init():
    """
    Test init a Portfolio with capital contribution report
    """
    with pytest.raises(Exception):
        init_fn = "test/data/distributions.tsv"
        portfolio = Portfolio(init_fn)
    init_fn = "test/data/contributions.tsv"
    portfolio = Portfolio(init_fn)
    assert len(portfolio.sponsors) == 2

    init_fn = "test/data/contributions.csv"
    portfolio = Portfolio(init_fn)
    assert len(portfolio.sponsors) == 2


if __name__ == "__main__":  # pragma: no cover
    test_init()
