import argparse
import math
from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd
import numpy as np
import yfinance as yf


@dataclass
class Trade:
    date: pd.Timestamp
    action: str
    delta: float
    entry: float
    exit: float
    profit: float


def black_scholes_price(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> float:
    """Calculate Black-Scholes option price."""
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if option_type == 'call':
        price = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    else:
        price = K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)
    return price


def black_scholes_delta(S: float, K: float, T: float, r: float, sigma: float, option_type: str) -> float:
    """Calculate Black-Scholes delta."""
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    if option_type == 'call':
        return norm_cdf(d1)
    else:
        return norm_cdf(d1) - 1


def norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def historical_volatility(returns: pd.Series, window: int = 30) -> pd.Series:
    return returns.rolling(window).std() * math.sqrt(252)


def backtest(ticker: str, start: str, end: str, expiry_days: int = 7, risk_free: float = 0.05) -> Tuple[pd.DataFrame, float, float]:
    data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    price_col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
    data['returns'] = np.log(data[price_col] / data[price_col].shift(1))
    data['vol'] = historical_volatility(data['returns'])
    data['sma'] = data[price_col].rolling(window=20).mean()
    trades: List[Trade] = []
    for i in range(len(data) - 1):
        row = data.iloc[i]
        next_row = data.iloc[i + 1]
        sigma = row['vol']
        sma = row['sma']
        if pd.isna(sigma) or pd.isna(sma):
            continue
        S = row[price_col]
        action = None
        option_type = 'call'
        if S > sma:
            action = 'buy_call'
            option_type = 'call'
        elif S < sma:
            action = 'buy_put'
            option_type = 'put'
        if action is None:
            continue
        K = S
        T = expiry_days / 365
        price_entry = black_scholes_price(S, K, T, risk_free, sigma, option_type)
        delta = black_scholes_delta(S, K, T, risk_free, sigma, option_type)
        # next day prices
        S_next = next_row[price_col]
        sigma_next = next_row['vol'] if not pd.isna(next_row['vol']) else sigma
        price_exit = black_scholes_price(S_next, K, T - 1/365, risk_free, sigma_next, option_type)
        trades.append(Trade(date=row.name, action=action, delta=delta, entry=price_entry, exit=price_exit, profit=price_exit - price_entry))
    df_trades = pd.DataFrame([t.__dict__ for t in trades])
    total_profit = df_trades['profit'].sum() if not df_trades.empty else 0.0
    win_rate = (df_trades['profit'] > 0).mean() * 100 if not df_trades.empty else 0.0
    return df_trades, total_profit, win_rate


def main() -> None:
    parser = argparse.ArgumentParser(description='Simple options backtester')
    parser.add_argument('ticker', help='Ticker symbol to backtest')
    parser.add_argument('--start', required=True, help='Backtest start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='Backtest end date (YYYY-MM-DD)')
    parser.add_argument('--expiry', type=int, default=7, help='Days to expiration for each trade')
    args = parser.parse_args()

    trades, total_profit, win_rate = backtest(args.ticker, args.start, args.end, args.expiry)

    print(trades)
    print(f'Total Profit: {total_profit:.2f}')
    print(f'Win Rate: {win_rate:.2f}%')


if __name__ == '__main__':
    main()
