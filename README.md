# BTUtils

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

BTUtils (Backtest Utilities) is a lightweight Python library for backtesting analysis and visualization of trading strategies. Inspired by the excellent [QuantStats](https://github.com/ranaroussi/quantstats) package, BTUtils provides a simplified and streamlined approach to analyze and visualize trading performance.

## Features

- Calculate key performance metrics:
  - Returns (cumulative, annual)
  - Risk metrics (volatility, drawdowns, VaR/CVaR)
  - Ratios (Sharpe, Sortino)
  - Alpha/Beta analysis
  - Win rate and payoff statistics

- Visualize strategy performance:
  - Cumulative returns with drawdowns
  - Return distribution analysis
  - Monthly/yearly heatmaps
  - Rolling metrics (volatility, Sharpe, Sortino, etc.)
  - Comparative analysis against benchmarks

## Installation

```bash
pip install btutils
```

## Quick Start

```python
import pandas as pd
import btutils
from btutils import Backtest

# Create a Backtest instance from a pandas Series of returns
returns = pd.Series(...)  # Your daily returns data
bt = Backtest(returns, name="My Strategy")

# Display key metrics
print(bt.metrics())

# Compare with a benchmark
benchmark = pd.Series(...)  # Benchmark returns
print(bt.metrics(index_list=[benchmark]))

# Visualize performance
bt.plots.line(benchmark=benchmark, show_drawdown=True)
bt.plots.hist()
bt.plots.heatmap(freq="ME")  # Monthly heatmap
bt.plots.rolling_sharpe(window=60)
```

## Documentation

The library consists of three main classes:
- `Backtest`: The main class for handling return series
- `Stats`: For calculating performance metrics
- `Plots`: For visualizing performance

## Requirements

- Python 3.13+
- pandas
- numpy
- matplotlib
- seaborn
- scipy

## License

MIT License

## Acknowledgements

BTUtils was inspired by [QuantStats](https://github.com/ranaroussi/quantstats) but with the goal of providing a more streamlined API focused on the most essential backtesting analytics.
