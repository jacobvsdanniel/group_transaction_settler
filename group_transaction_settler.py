import csv
import sys
import heapq
import logging
import argparse

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


class Settler:
    def __init__(self):
        self.account_list = []
        self.account_to_index = {}
        self.credit_list = []
        return

    def process_transaction(self, account, transaction):
        if transaction > 0:
            # when Alice paid money in real life, her account gains credit
            logger.info(f"[transaction] {account} paid ${transaction:,g}")

        elif transaction < 0:
            # when Bob received money in real life, his account loses credit
            logger.info(f"[transaction] {account} receive ${-transaction:,g}")

        index = self.account_to_index.get(account, None)
        if index is None:
            index = len(self.account_list)
            self.account_list.append(account)
            self.account_to_index[account] = index
            self.credit_list.append(transaction)
        else:
            self.credit_list[index] += transaction
        return

    def read_transactions(self, transaction_list=None, transaction_file=None):
        if transaction_list is not None:
            for account, transaction in transaction_list:
                self.process_transaction(account, transaction)
            return

        if transaction_file is not None:
            with open(transaction_file, "r", encoding="utf8", newline="") as f:
                reader = csv.reader(f, dialect="csv")
                header = next(reader)
                assert header == ["account", "transaction"]
                for account, transaction in reader:
                    transaction = float(transaction)
                    self.process_transaction(account, transaction)
            return

    def get_settlements(self, settlement_file=None):
        # show current account credits
        logger.info("account credits before settlements:")
        for account, credit in sorted(zip(self.account_list, self.credit_list), key=lambda ac: (-ac[1], ac[0])):
            logger.info(f"[credit] {account} net worth ${credit:,g}")

        # prepare sorted credits and debts
        positive_credit_heap = []  # min-heap of (-credit, account index)
        negative_credit_heap = []  # min-heap of (credit, account index)
        for index, credit in enumerate(self.credit_list):
            if credit > 0:
                heapq.heappush(positive_credit_heap, (-credit, index))
            elif credit < 0:
                heapq.heappush(negative_credit_heap, (credit, index))

        # calculate settlements
        settlement_list = []  # a list of (sending account, receiving account, settlement amount)
        while True:
            # the account with the most debt should pay the account with the most credit
            try:
                negated_credit, receiver_account_index = heapq.heappop(positive_credit_heap)
                negated_debt, sender_account_index = heapq.heappop(negative_credit_heap)
            except IndexError:
                # no more settlements can be made if there are no positive accounts or no negative accounts
                break
            sender_account = self.account_list[sender_account_index]
            receiver_account = self.account_list[receiver_account_index]

            # the settlement is the sender's debt
            settlement = -negated_debt
            settlement_list.append((sender_account, receiver_account, settlement))
            logger.info(f"[settlement] {sender_account} should pay ${settlement:,g} to {receiver_account}")

            # update receiver account
            receiver_credit = -negated_credit - settlement
            if receiver_credit > 0:
                heapq.heappush(positive_credit_heap, (-receiver_credit, receiver_account_index))
            elif receiver_credit < 0:
                heapq.heappush(negative_credit_heap, (receiver_credit, receiver_account_index))

        # show future account credits if settlements are made
        logger.info("if these settlements are made, account credits will be:")
        future_credit_list = [0] * len(self.credit_list)
        for negated_credit, account_index in positive_credit_heap:
            future_credit_list[account_index] = -negated_credit
        for credit, account_index in negative_credit_heap:
            future_credit_list[account_index] = credit
        for account, credit in sorted(zip(self.account_list, future_credit_list), key=lambda ac: (-ac[1], ac[0])):
            logger.info(f"[credit] {account} net worth ${credit:,g}")

        # write to file
        if settlement_file is not None:
            with open(settlement_file, "w", encoding="utf8", newline="") as f:
                writer = csv.writer(f, dialect="csv")
                header = ["sender", "receiver", "settlement"]
                writer.writerow(header)
                for sending_account, receiving_account, settlement_amount in settlement_list:
                    writer.writerow([sending_account, receiving_account, f"{settlement_amount:g}"])
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
    settler.read_transactions(transaction_file=arg.transaction_file)
    settler.get_settlements(settlement_file=arg.settlement_file)
    return


if __name__ == "__main__":
    main()
    sys.exit()
