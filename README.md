# Stock Screener

This project is a stock screener that helps identify potential trading opportunities based on specific criteria.

## Overview

The stock screener analyzes a list of stock symbols and filters them based on predefined conditions. It uses historical stock data and calculates various indicators to determine whether a stock should be considered for long or short positions.

## Features

- **Stock Screening**: The program fetches historical stock data using the Yahoo Finance API, calculates percentage returns, and screens stocks based on user-defined threshold values.
- **Pivot Calculation**: The program calculates pivot points for short-listed stocks to identify potential support and resistance levels.
- **Order Placement**: The program places buy/sell orders for stocks that meet specific criteria, such as open price, previous day's high/low, resistance/support levels, and percentage change.

## Setup

1. Clone the repository: `git clone <repository_url>`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Configure the settings in the `config.yaml` file, including threshold values, target time, starting capital, and other parameters.
4. Provide a list of stock symbols in the `data/universe.csv` file.
5. Run the main script: `python main.py`

## Configuration

The `config.yaml` file contains various settings and parameters for the stock screener. You can modify these values according to your requirements. Here are the key configuration options:

- `threshold_positive`: The threshold percentage for identifying stocks with positive returns. Currently set to: 4.7
- `threshold_negative`: The threshold percentage for identifying stocks with negative returns. Currently set to: -4.7
- `target_time`: The target time to start scanning for potential trades. Currently set to: '09:14:00'
- `order_execution_time`: The time at which the orders should be executed. Currently set to: '09:15:00'
- `share_price_min_threshold`: The minimum price for share to considered. Currently set to: 50
- `share_price_max_threshold`: The maximum price for share to considered. Currently set to: 3000
- `stop_loss`: The stop loss percentage for trades. Currently set to: 0.01
- `target1`: The first target percentage for trades. Currently set to: 0.005
- `target2`: The second target percentage for trades. Currently set to: 0.075
- `target3`: The third target percentage for trades. Currently set to: 0.01
- `capital`: The initial amount of capital available for trading. Currently set to: 1000
- `buffer_entry`: The buffer percentage for entry prices. Currently set to: 0.001
- `buffer_trigger`: The buffer percentage for trigger prices. Currently set to: 0.05

You can update these values in the `config.yaml` file based on your requirements.


## Results

After running the script, the program will generate a DataFrame with the short-listed stocks and their respective pivot points. The program will also place buy/sell orders for stocks that meet the specified conditions.
