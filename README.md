## yahoo-finance-ledger-cli

Grab historical stock prices from Yahoo Finance and output in Ledger CLI format.


### How to use

Create a Python 3 virtual environment, activate it,
and install the packages from `requirements.txt`.

Create a text file named `.config` at the repository root,
and include any stock symbols you'd like to get price information for.
Institution and account names will be included in the output
to group the returned information (as shown below).

To execute the script run `python main.py 2023-05-10 -v`.
The verbose flag is optional, though useful
if there are many symbols to process (to interactively view progress).
The output is saved in an `output.txt` file by default.

Example `.config` file:

```
Institution:
  AccountName:
    - AAPL
    - MSFT
    - AMZN
    - GOOGL
    - FB
```

The generated `output.txt`:

```
; Institution
; AccountName
P 2023/05/10            AAPL           USD    173.56
P 2023/05/10            MSFT           USD    312.31
P 2023/05/10            AMZN           USD    110.19
P 2023/05/10            GOOGL          USD    111.75
P 2023/05/10            FB             USD    233.08
```
