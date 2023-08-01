"""
Unit tests
"""

from cstreet.finances import Portfolio


def test_init():
    """
    Test init a Portfolio with capital contribution report
    """
    init_fn = "test/data/init.tsv"
    portfolio = Portfolio(init_fn)
    assert len(portfolio.sponsors) == 2


if __name__ == "__main__":
    test_init()
