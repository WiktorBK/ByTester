
# ByTester

Program using technical analysis, showing great opportunities to place an order on the online cryptocurrency exchange. Includes backtests checking reliability of certain strategy.


## How does it work?

Program gathers past data from bybit's api and based on that checks the reliability of **EMA cross** strategy. ByTester checks for possible crosses and predicts how the trades would have ended. Changing the params such as: **Ema windows, timeframe, leverage, capital or border prices** user can test out the strategy in various configurations.
## Installation

- Create virutal environment
- `git clone https://github.com/WiktorBK/ByTester.git`
- `pip install -r requirements.txt`

Configure your bot inside `config.py` file.
## Usage

After installing the program enter this command:

`run.py`


Example output:
~~~
SOLUSDT {'start_date': Timestamp('2023-04-18 06:45:00'), 
'end_date': Timestamp('2023-05-15 02:30:00'), 
'wins': 20, 'losses': 13, 'till_next_cross': 6,
'profit': 0.827, 'minus': 19, 'plus': 20}
~~~


## Authors

- [@Wiktor Bożek](https://www.github.com/WiktorBK)


## License

[MIT](https://github.com/WiktorBK/ByTester/blob/master/LICENSE) 

