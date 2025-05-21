# Group Transaction Settler

### Usage
```
python group_transaction_settler.py --transaction_file transaction.csv --settlement_file settlement.csv
```

### Example scenario
First, at a restaurant, Alice ordered a meal priced at $100; Bob ordered a meal priced at $150; Cindy ordered a meal priced at $200. When paying the bill, Alice paid $200; Cindy paid 250.

Then, at a resort, Alice ordered a ride priced at $300; Bob ordered a ride priced at $200; Cindy ordered a ride priced at $200. When paying the bill, Alice paid $250; Bob paid 450.

Afterwards, how should they settle these events, preferably everyone makes at most one payment?

Prepare the input transaction file:
```
account,transaction
Alice,-100
Bob,-150
Cindy,-200
Alice,200
Cindy,250
Alice,-300
Bob,-200
Cindy,-200
Alice,250
Bob,450
```

Run
```
python group_transaction_settler.py --transaction_file example_1/transaction.csv --settlement_file example_1/settlement.csv
```

The output settlement file:
```
sender,receiver,settlement
Cindy,Bob,150
Bob,Alice,50
```

Now they know Cindy should send Bob $150, and Bob should send Alice $50. This way, everyone pays what they owe and with at most one payment.

See example_2 for another, more complex, example.
