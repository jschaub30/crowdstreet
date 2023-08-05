"""
Generate TSV table of Crowdstreet portfolio for each year of it's existence
"""
from datetime import date

from crowdstreet import Portfolio


def main():
    """ Analyze portfolio by year """
    portfolio = Portfolio("path_to_contritions_file.csv")
    portfolio.read_distributions("path_to_distributions_file.csv")

    print(
        "YEAR\tCapital Committed\tCapital Contributed\tCapital Balance\t" +
        "Return of Capital\tReturn on Capital"
    )
    for year in range(portfolio.start_date.year, date.today().year + 1):
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        rofc = portfolio.return_of_capital(start_date=start_date, end_date=end_date)
        ronc = portfolio.return_on_capital(start_date=start_date, end_date=end_date)
        ccom = portfolio.capital_committed(end_date=end_date)
        ccon = portfolio.capital_contributed(end_date=end_date)
        cbal = portfolio.capital_balance(end_date=end_date)
        print(
            f"{year}\t${ccom:16.2f}\t${ccon:17.2f}\t${cbal:14.2f}\t"
            + f"${rofc:16.2f}\t${ronc:16.2f}"
        )
    rofc = portfolio.return_of_capital()
    ronc = portfolio.return_on_capital()
    ccom = portfolio.capital_committed()
    ccon = portfolio.capital_contributed()
    cbal = portfolio.capital_balance()
    print(
        f"TOTAL\t${ccom:16.2f}\t${ccon:17.2f}\t${cbal:14.2f}\t"
        + f"${rofc:16.2f}\t${ronc:16.2f}"
    )


if __name__ == "__main__":
    main()
