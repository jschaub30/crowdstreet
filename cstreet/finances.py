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
            LOGGER.info(f"Reading contribution data from {fname!r}")
            if fname.endswith("tsv"):
                delimiter = "\t"
            elif fname.endswith("csv"):  # pragma: no cover
                delimiter = ","
            else:  # pragma: no cover
                raise Exception(f"Unknown extension for {fname!r}")
            csv_file = csv.DictReader(fid, delimiter=delimiter)
            for line in csv_file:
                if "Capital Contribution Amount" not in line:
                    raise Exception(
                        f"{fname!r} does not appear to be a Crowdstreet Capital " +
                        "Contribution report"
                    )
                LOGGER.debug(
                    f"Adding {line['Capital Contribution Amount']} transaction " +
                    f"from sponsor={line['Sponsor']!r} " +
                    f"on offering={line['Offering']!r} "
                )
                self.offerings.add(line["Offering"])
                self.sponsors.add(line["Sponsor"])
                self._transactions.append("TBD contribution")

    def add_distributions(self, fname):
        """
        Add data from "Distributions" report
        """
        with open(fname, "r", encoding=ENCODING) as fid:
            LOGGER.info(f"Adding distributions from {fname!r}")
            if fname.endswith("tsv"):
                delimiter = "\t"
            elif fname.endswith("csv"):  # pragma: no cover
                delimiter = ","
            else:  # pragma: no cover
                raise Exception(f"Unknown extension for {fname!r}")
            csv_file = csv.DictReader(fid, delimiter=delimiter)
            for line in csv_file:
                if "Distribution ID" not in line:
                    raise Exception(
                        f"{fname!r} does not appear to be a Crowdstreet Distribution report"
                    )
                if line['Sponsor'] not in self.sponsors:
                    raise Exception(f"Sponsor {line['Sponsor']!r} not one of {self.sponsors}")
                if line['Offering'] not in self.offerings:
                    raise Exception(f"Offering={line['Offering']!r} not one of {self.offerings}")
                self._transactions.append("TBD distribution")


    def capital_balance(self, investing_entity=None, sponsor=None, offering=None):
        """ Return capital balance """
        return 0

    def transactions(self, start_date=None, end_date=None):
        """ Return list of transactions in portfolio """
        return self._transactions
