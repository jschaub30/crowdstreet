"""
Classes for reading and analyzing Crowdstreet transactions
"""
from datetime import datetime, date
from logging import getLogger
from pathlib import Path
import csv

LOGGER = getLogger()
ENCODING = "utf8"


class Transaction:
    """
    Transactions can be either:
    - contributions (investments)
    - distributions, in 2 flavors:
      - return ON capital
      - return OF capital

    Common properties:
    - sponsor
    - offering
    - investing_entity
    - transaction_type ("Contribution" or "Distribution")
    - description
    - id
    - date: either "Period End Date" or "Transaction Date"

    "Contribution"-specific properties:
    - capital_contribution (negative number)

    "Distribution"-specific properties:
    - total_distribution
    - return_on_capital
    - return_of_capital
    """

    def __init__(self, line):
        """
        line is a dict read from either a contribution report or distribution report
        """
        self.sponsor = line["Sponsor"]
        self.offering = line["Offering"]
        self.investing_entity = line["Investing Entity"]
        if "Capital Contribution Amount" in line:  # contribution
            self.transaction_type = "Contribution"
            self.description = line["Transaction Description"]
            self.id = int(line["Capital Contribution ID"])
            datestr = line["Transaction Date"]
            self.date = datetime.strptime(datestr, "%Y-%m-%d").date()
            # contributions are negative
            self.capital = -float(line["Capital Contribution Amount"])
            msg = f"Adding ${self.capital:11.02f} {self.transaction_type} "
        if "Return on Capital" in line:  # distribution
            self.transaction_type = "Distribution"
            self.description = line["Description"]
            self.id = int(line["Distribution ID"])
            datestr = line["Period End Date"]
            self.date = datetime.strptime(datestr, "%Y-%m-%d").date()
            datestr = line["Period End Date"]
            self.distribution_date = datetime.strptime(datestr, "%Y-%m-%d").date()
            self.total_distribution = float(line["Total Distribution"])
            val = line["Return of Capital"]
            self.return_of_capital = float(val) if val else 0
            self.capital = self.return_of_capital
            val = line["Return on Capital"]
            self.return_on_capital = float(val) if val else 0
            val = line["Withholdings"]
            self.withholdings = float(val) if val else 0
            msg = f"Adding ${self.total_distribution:11.02f} {self.transaction_type} "
        LOGGER.debug(msg + f"from {self.sponsor!r} on {self.offering!r} offering")

    def __repr__(self):
        return f"{self.date}  {self.transaction_type}  ${self.capital:10.02f}"


class Portfolio:
    """
    Portfolio of Crowdstreet investments
    """

    def __init__(self, fname):
        """
        Init with "Capital Contribution report"
        """
        self.sponsors = set()
        self.offerings = set()
        self.investing_entities = set()
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
                        f"{fname!r} does not appear to be a Crowdstreet Capital "
                        + "Contribution report"
                    )
                self.offerings.add(line["Offering"])
                self.sponsors.add(line["Sponsor"])
                self.investing_entities.add(line["Investing Entity"])
                ids = [t.id for t in self.transactions()]
                txn = Transaction(line)
                if txn.id in ids:
                    LOGGER.warning(f"Skipping duplicate transaction: {txn}")
                    continue
                self._transactions.append(txn)

    def read_distributions(self, fname):
        """
        Add data from "Distributions" report to portfolio
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
                if line["Sponsor"] not in self.sponsors:
                    raise Exception(
                        f"Sponsor {line['Sponsor']!r} not one of {self.sponsors}"
                    )
                if line["Offering"] not in self.offerings:
                    raise Exception(
                        f"Offering={line['Offering']!r} not one of {self.offerings}"
                    )
                if (
                    line["Investing Entity"] not in self.investing_entities
                ):  # pragma: no cover
                    raise Exception(
                        f"Entity {line['Investing Entity']!r} not one of {self.investing_entities}"
                    )
                ids = [t.id for t in self.transactions()]
                txn = Transaction(line)
                if txn.id in ids:
                    LOGGER.warning(f"Skipping duplicate transaction: {txn}")
                    continue
                self._transactions.append(txn)

    def capital_contributed(self, **kwargs):
        """
        Return capital contributed as float.
        """
        txns = self.transactions(**kwargs)
        txns = [
            t
            for t in self.transactions(**kwargs)
            if t.transaction_type == "Contribution"
        ]
        return round(sum([t.capital for t in txns]), 2)

    def capital_balance(self, **kwargs):
        """
        Return capital balance as float.
        """
        txns = self.transactions(**kwargs)
        return round(sum([t.capital for t in txns]), 2)

    def return_of_capital(self, **kwargs):
        """
        Return sum of capital returned float
        """
        txns = [
            t
            for t in self.transactions(**kwargs)
            if t.transaction_type == "Distribution"
        ]
        return round(sum([t.return_of_capital for t in txns]), 2)

    def return_on_capital(self, **kwargs):
        """
        Return sum of return on capital as float
        """
        txns = [
            t
            for t in self.transactions(**kwargs)
            if t.transaction_type == "Distribution"
        ]
        return round(sum([t.return_on_capital for t in txns]), 2)

    def distributions(self, **kwargs):
        """
        Return sum of total distributions as float
        """
        txns = [
            t
            for t in self.transactions(**kwargs)
            if t.transaction_type == "Distribution"
        ]
        return round(sum([t.total_distribution for t in txns]), 2)

    def transactions(self, **kwargs):
        """
        Return list of transactions in portfolio
        If no keyword args are provided, return all transactions

        Keyword arguments:
        investing_entity:  str
        sponsor:           str
        offering:          str
        end_date:          datetime.date Only include trasacations up until this date
                           (inclusive)
        """
        txns = self._transactions
        for attr in ("investing_entity", "sponsor", "offering"):
            if attr in kwargs and kwargs.get(attr) is not None:
                txns = [t for t in txns if getattr(t, attr) == kwargs.get(attr)]
        if "end_date" in kwargs and kwargs.get("end_date"):
            end_date = kwargs.get("end_date")
        else:
            end_date = date.today()
        txns = [t for t in txns if t.date <= end_date]
        return txns

    HEADER = [
        "Entity",
        "Offering",
        "Capital Contributed",
        "Capital Balance",
        "Total Distributed",
        "Return of Capital",
        "Return on Capital",
        "As of date",
    ]

    def _summary(self, verbose, end_date):
        """
        Return portfolio summary as list

        Keyword arguments:
        verbose:  int (default = 2)
          0:  top level summary of total portfolio
          1:  summarize each investment entity individually
          2:  summarize each offering individually
        """
        rows = []
        if end_date:
            datestr = end_date.strftime("%Y-%m-%d")
        else:
            datestr = date.today().strftime("%Y-%m-%d")
        if verbose == 0:
            entities = [None]
            offerings = [None]
        elif verbose == 1:
            entities = sorted(self.investing_entities)
            offerings = [None]
        elif verbose == 2:
            entities = sorted(self.investing_entities)
            offerings = sorted(self.offerings)

        for entity in entities:
            for offering in offerings:
                cc = self.capital_contributed(
                    investing_entity=entity, offering=offering, end_date=end_date
                )
                if not cc:
                    continue
                cb = self.capital_balance(
                    investing_entity=entity, offering=offering, end_date=end_date
                )
                dist = self.distributions(
                    investing_entity=entity, offering=offering, end_date=end_date
                )
                rofc = self.return_of_capital(
                    investing_entity=entity, offering=offering, end_date=end_date
                )
                ronc = self.return_on_capital(
                    investing_entity=entity, offering=offering, end_date=end_date
                )
                entity = "ALL" if not entity else entity
                offering = "ALL" if not offering else offering
                rows.append([entity, offering, cc, cb, dist, rofc, ronc, datestr])
        return rows

    def save_summary(self, fname, delimiter="\t", verbose=2, end_date=None):
        """
        Save portfolio summary to delimited file

        Positional arguments:
        fname:  str  filename

        Keyword arguments:
        delimiter: str (default = "\t")
        verbose:   int (default = 2)
          0:  top level summary of total portfolio
          1:  summarize each investment entity individually
          2:  summarize each offering individually
        """
        rows = [self.HEADER] + self._summary(verbose, end_date)
        Path(fname).parent.mkdir(parents=True, exist_ok=True)
        with open(fname, "w", encoding=ENCODING) as fid:
            csv_file = csv.writer(
                fid, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            for row in rows:
                csv_file.writerow(row)
        LOGGER.info(f"Summary written to {fname!r}")
