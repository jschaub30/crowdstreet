"""
Classes for reading and analyzing Crowdstreet transactions
"""
from datetime import datetime
from logging import getLogger
import csv

LOGGER = getLogger()
ENCODING = "utf8"


class Transaction():
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
    - amount: either "Capital Contribution" (negative) or "Total Distribution" (positive)
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
            self.amount = - float(line["Capital Contribution Amount"])
            self.distribution = 0
            amount = self.amount
        if "Return on Capital" in line:  # distribution
            self.transaction_type = "Distribution"
            self.description = line["Description"]
            self.id = int(line["Distribution ID"])
            datestr = line["Period End Date"]
            self.date = datetime.strptime(datestr, "%Y-%m-%d").date()
            datestr = line["Period End Date"]
            self.distribution_date = datetime.strptime(datestr, "%Y-%m-%d").date()
            self.distribution = float(line["Total Distribution"])
            val = line["Return of Capital"]
            self.return_of_capital = float(val) if val else 0
            val = line["Return on Capital"]
            self.return_on_capital = float(val) if val else 0
            self.amount = self.return_of_capital
            val = line["Withholdings"]
            self.withholdings = float(val) if val else 0
            amount = self.distribution
        LOGGER.debug(
            f"Adding ${amount:10.02f} {self.transaction_type} " +
            f"from {self.sponsor!r} " +
            f"on {self.offering!r} offering"
        )

    def __repr__(self):
        return f"{self.date}  {self.transaction_type}  ${self.amount:10.02f}"


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
                        f"{fname!r} does not appear to be a Crowdstreet Capital " +
                        "Contribution report"
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
                if line['Investing Entity'] not in self.investing_entities:  # pragma: no cover
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
        """ Return capital balance """
        txns = self.transactions(**kwargs)
        txns = [t for t in self.transactions(**kwargs) if t.transaction_type == "Contribution"]
        return round(sum([t.amount for t in txns]), 2)

    def capital_balance(self, **kwargs):
        """ Return capital balance """
        txns = self.transactions(**kwargs)
        return round(sum([t.amount for t in txns]), 2)

    def distributions(self, **kwargs):
        txns = [t for t in self.transactions(**kwargs) if t.transaction_type == "Distribution"]
        return round(sum([t.amount for t in txns]), 2)

    def transactions(self, **kwargs):
        """ Return list of transactions in portfolio """
        txns = self._transactions
        for attr in ("investing_entity", "sponsor", "offering"):
            if attr in kwargs:
                txns = [t for t in txns if getattr(t, attr) == kwargs.get(attr)]
        if "start_date" in kwargs:
            txns = [t for t in txns if t.date >= kwargs.get("start_date")]
        if "end_date" in kwargs:
            txns = [t for t in txns if t.date <= kwargs.get("end_date")]
        return txns

    def summary(self):
        """
        This mimics the table shown in the Crowdstreet dashboard
        """
        msg = f"{'TOTAL':80}\t${self.capital_contributed():12.2f}\n"
        for entity in self.investing_entities:
            msg += f"  {entity:78}\t${self.capital_contributed(investing_entity=entity):12.2f}\n"
            for offering in self.offerings:
                val = self.capital_contributed(investing_entity=entity, offering=offering)
                if not val:
                    continue
                msg += f"    {offering:76}\t${val:12.2f}\n"
        return msg
