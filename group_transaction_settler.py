import csv
import sys
import copy
import logging
import argparse
from collections import defaultdict

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
    level=logging.INFO,
)
csv.register_dialect(
    "csv", delimiter=",", quoting=csv.QUOTE_MINIMAL, quotechar='"', doublequote=True,
    escapechar=None, lineterminator="\n", skipinitialspace=False,
)


def show_balance(account_to_credit):
    for account, credit in sorted(account_to_credit.items(), key=lambda nc: (-nc[1], nc[0])):
        logger.info(f"[credit] {account} net worth ${credit:,g}")
    return


def write_settlements_to_csv_file(settlement_list, settlement_csv_file):
    with open(settlement_csv_file, "w", encoding="utf8", newline="") as f:
        writer = csv.writer(f, dialect="csv")
        header = ["sender", "receiver", "settlement"]
        writer.writerow(header)
        for sending_account, receiving_account, settlement_amount in settlement_list:
            writer.writerow([sending_account, receiving_account, f"{settlement_amount:g}"])
    return


class Settler:
    def __init__(self):
        self.account_to_credit = defaultdict(lambda: 0)
        return

    def process_transaction(self, account, transaction):
        if transaction > 0:
            # when Alice paid money in real life, her account gains credit
            logger.info(f"[transaction] {account} paid ${transaction:,g}")

        elif transaction < 0:
            # when Bob received money in real life, his account loses credit
            logger.info(f"[transaction] {account} receive ${-transaction:,g}")

        self.account_to_credit[account] += transaction
        return

    def read_transactions(self, transaction_list):
        for account, transaction in transaction_list:
            self.process_transaction(account, transaction)
        return

    def read_transactions_from_csv_file(self, transaction_file):
        with open(transaction_file, "r", encoding="utf8", newline="") as f:
            reader = csv.reader(f, dialect="csv")
            header = next(reader)
            assert header == ["account", "transaction"]
            for account, transaction in reader:
                transaction = float(transaction)
                self.process_transaction(account, transaction)
        return

    def get_settlements(self):
        logger.info("account credits before settlements:")
        show_balance(self.account_to_credit)

        # calculate settlements
        account_to_credit = copy.deepcopy(self.account_to_credit)
        settlement_list = []
        while True:
            # collect accounts that have positive/negative credits
            positive_credit_account_list = []
            negative_credit_account_list = []
            for account, credit in account_to_credit.items():
                if credit > 0:
                    positive_credit_account_list.append((credit, account))
                elif credit < 0:
                    negative_credit_account_list.append((-credit, account))

            # no more settlements can be made if there are no positive accounts or no negative accounts
            if not positive_credit_account_list or not negative_credit_account_list:
                break

            # the account with the most debt should pay the account with the most credit
            _, max_credit_account = max(positive_credit_account_list)
            settlement, max_debt_account = max(negative_credit_account_list)
            settlement_list.append((max_debt_account, max_credit_account, settlement))
            account_to_credit[max_debt_account] += settlement
            account_to_credit[max_credit_account] -= settlement
            logger.info(f"[settlement] {max_debt_account} should pay ${settlement:,g} to {max_credit_account}")

        logger.info("if these settlements are made, account credits with be:")
        show_balance(account_to_credit)

        return settlement_list

    def get_settlements_and_write_to_csv_file(self, settlement_file):
        settlement_list = self.get_settlements()
        write_settlements_to_csv_file(settlement_list, settlement_file)
        return settlement_list


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transaction_file", type=str)
    parser.add_argument("--settlement_file", type=str)
    arg = parser.parse_args()
    for key, value in vars(arg).items():
        if value is not None:
            logger.info(f"[arg.{key}] {value}")

    settler = Settler()
    settler.read_transactions_from_csv_file(arg.transaction_file)
    settler.get_settlements_and_write_to_csv_file(arg.settlement_file)
    return


if __name__ == "__main__":
    main()
    sys.exit()
