"""
Classes for reading and analyzing Crowdstreet transactions
"""
from logging import getLogger
import csv

LOGGER = getLogger()
ENCODING = "utf8"


class Portfolio():
    """
    Portfolio of Crowdstreet investments
    """

    def __init__(self, fname):
        """
        Init with "Capital Contribution report"
        """
        self.sponsors = set()
        self.offerings = set()
        self._transactions = []
        with open(fname, "r", encoding=ENCODING) as fid:
            LOGGER.info(f"Reading {fname}")
            if fname.endswith("tsv"):
                delimiter = "\t"
            elif fname.endswith("csv"):
                delimiter = ","
            else:
                raise Exception(f"Unknown extension for {fname!r}")
            csv_file = csv.DictReader(fid, delimiter=delimiter)
            for line in csv_file:
                assert "Capital Contribution Amount" in line, fname
                LOGGER.debug(
                    f"Adding {line['Capital Contribution Amount']} transaction " +
                    f"from sponsor={line['Sponsor']!r} " +
                    f"on offering={line['Offering']!r} "
                )
                self.offerings.add(line["Offering"])
                self.sponsors.add(line["Sponsor"])
