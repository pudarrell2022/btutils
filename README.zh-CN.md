# BTUtils

[中文](README.zh-CN.md) | [English](README.md)

[![Python 版本](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 简介

BTUtils（Backtest Utilities）是一个轻量级 Python 库，用于回测分析与交易策略可视化。受 [QuantStats](https://github.com/ranaroussi/quantstats) 启发，BTUtils 提供更简洁的接口，专注于核心回测分析功能。

## 功能

- **核心绩效指标**：
  - 收益（累计、年化）
  - 风险指标（波动率、回撤、VaR/CVaR）
  - 比率（夏普、索提诺）
  - 阿尔法/贝塔分析
  - 胜率与盈亏比统计

- **策略表现可视化**：
  - 累计收益与回撤
  - 收益分布分析
  - 月度/年度热力图
  - 滚动指标（波动率、夏普、索提诺等）
  - 与基准的对比分析

## 安装

```bash
pip install btutils
```

从源码进行开发安装：

```bash
git clone https://github.com/yourusername/btutils.git
cd btutils
pip install -e .
```

## 指标报告

```python
import pandas as pd
from btutils import Backtest

# 用收益序列创建 Backtest 实例
returns = pd.Series(...)  # 你的日收益数据
bt = Backtest(returns, name="我的策略")

# 输出核心指标
print(bt.metrics())
```

示例输出：
```
Start Date             2015-04-27
End Date               2025-05-26
Time in Market %           99.55%
Annual Return %            24.13%
Annual Volatility %        30.33%
Sharpe Ratio                 0.75
Max Drawdown %            -47.48%
Win Rate %                 49.69%
Payoff Rate               118.01%
dtype: object
```

## 绩效指标

```python
# 计算单项指标
sharpe = bt.stats.sharpe_ratio()
max_dd = bt.stats.max_drawdown()
sortino = bt.stats.sortino_ratio()
beta = bt.stats.beta(benchmark)
alpha = bt.stats.alpha(benchmark)

# 最佳与最差区间
best_days = bt.stats.best(freq="D", num=5)
worst_months = bt.stats.worst(freq="ME", num=3)

# 查看所有可用指标方法
print([method for method in dir(bt.stats) if not method.startswith("_")])
```

## 序列变换

```python
# 对收益序列做变换
drawdowns = bt.to_drawdown()
cumulative = bt.to_cumulative_return()

# 按日期切片
ytd = bt.slice_date('ytd')  # 年初至今
specific_period = bt.slice_date('20200101', '20241231')

# 滚动指标
rolling_vol = bt.to_rolling_volatility(window=60)
rolling_sharpe = bt.to_rolling_sharpe(window=60)
```

## 可视化

### 累计收益与回撤

```python
bt.plots.line(benchmark=benchmark, show_drawdown=True, worst_num=2)
```

![](docs/line.png)

### 月度收益柱状图

```python
bt.plots.bar(freq="ME")
```

![](docs/bar.png)

### 收益分布直方图

```python
bt.plots.hist()
```

![](docs/hist.png)

### 按时间维度的收益分布

```python
bt.plots.dist()
```

![](docs/dist.png)

### 月度收益热力图

```python
bt.plots.heatmap(freq="ME")
```

![](docs/heatmap.png)

### 滚动夏普比率

```python
bt.plots.rolling_sharpe()
```

![](docs/rolling_sharpe.png)

## 文档说明

库主要由三个类组成：
- `Backtest`：处理收益序列的主类
- `Stats`：计算绩效指标
- `Plots`：绩效可视化

查看所有方法可使用以下代码，完整文档将后续发布。
```python
print([_ for _ in dir(bt.stats) if not _.startswith("_")])
```

## 依赖

- Python 3.7+
- pandas
- numpy
- matplotlib
- seaborn
- scipy

## 许可证

MIT License

## 致谢

BTUtils 受 [QuantStats](https://github.com/ranaroussi/quantstats) 启发，旨在提供更精简的 API，聚焦最核心的回测分析功能。
