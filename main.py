import argparse
import datetime
import re
import yaml

import requests
from bs4 import BeautifulSoup


def load_configuration(file='.config'):
    """
    Load configuration from YAML file.

    Format is like:

    Institution:
      AccountName:
        - AAPL
        - MSFT
        - AMZN
        - GOOGL
        - FB

    There can be any number of institutions and accounts specified.

    """
    # Disclaimer: The stocks listed above are examples only,
    # and are not to be taken as a recommendation or endorsement.
    with open(file, 'r') as f:
        return yaml.safe_load(f)


def format_stock_price(date_str, symbol, currency, price):
    # The date string is formatted like '2023-05-10', but we want to output like '2023/05/10'.
    #
    # For the output line,
    #  the symbol starts at col 25, (so date width will be 25, less 2 (for 'P '), less 1 (ends at col 39))
    #  currency at col 40, (so symbol width will be 15)
    #  price decimal is placed at col 50. (so currency width will be 10 less space in front of decimal)
    #
    return f"P {date_str.replace('-', '/'):<22}{symbol:<15}{currency:<{10 - price.index('.')}}{price}"


def get_stock_price(symbol, date_str):
    """Return currency and price as a tuple."""
    url = f'https://ca.finance.yahoo.com/quote/{symbol}/history'
    firefox_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13.5; rv:109.0) Gecko/20100101 Firefox/117.0'

    response = requests.get(url, headers={'User-Agent': firefox_user_agent})

    soup = BeautifulSoup(response.content, 'html.parser')
    date_text = datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime('%b %d, %Y')

    date_span = soup.find('span', string=date_text)

    if date_span is None:
        raise ValueError(f'No data available for {symbol} on {date_str}.')

    # TODO, There doesn't seem to be a way to do a named capture group for the currency code.
    currency_span = soup.find('span', string=re.compile(r'^Currency in \w{3}'))
    currency = currency_span.contents[0].string[-3:]

    price = (date_span
        .parent
        .next_sibling
        .next_sibling
        .next_sibling
        .next_sibling
        .contents[0]
        .string
    )

    return currency, f'{float(price):.2f}'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=(
        'Get historical price information for given stock symbols '
        'and return the data in a format suitable for Ledger CLI.'
    ))
    parser.add_argument('date', metavar='YYYY-MM-DD', type=str, help='A date in the format YYYY-MM-DD.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output.')
    parser.add_argument(
        '--output-file', '-o',
        dest='output', metavar='output.txt',
        type=str, default='output.txt',
        help='Output file name, defaults to `output.txt`.'
    )

    args = parser.parse_args()

    data = load_configuration()

    output = []
    for institution in data.keys():
        if args.verbose:
            print(f'Processing `{institution}` institution..')

        output.append(f'; {institution}')

        for account in data[institution].keys():
            output.append(f'; {account}')
            for symbol in data[institution][account]:
                currency, price = get_stock_price(symbol, args.date)
                output.append(format_stock_price(args.date, symbol, currency, price))

    with open(args.output, 'w') as f:
        f.write('\n'.join(output))
        if args.verbose:
            print(f'Output successfully written to {args.output}.')
