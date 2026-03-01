# AGENTS 指南

## 项目定位
`btutils` 是一个用于量化策略回测分析与可视化的 Python 库，核心能力是：
- 计算收益、风险、比率等绩效指标；
- 基于收益序列输出图表（累计收益、热力图、分布、滚动夏普等）；
- 通过 `Backtest`/`Stats`/`Plots` 三个类组织 API。

主要输入是 `pandas.Series` 形式的收益序列，输出是指标结果（数值/表格）与 Matplotlib 图形。

## 仓库结构与职责
- `btutils/btutils.py`：主实现文件，包含 `Stats`、`Plots`、`Backtest`。
- `btutils/__init__.py`：包导出与元信息（版本、作者、许可证）。
- `docs/`：README 使用的示例图资源。
- `README.md`、`README.zh-CN.md`：中英文说明与示例代码。
- `pyproject.toml`：项目元数据与依赖（`matplotlib`、`pandas`、`scipy`、`seaborn`、`tabulate`）。
- `uv.lock`：依赖锁文件（基于 `uv`）。

## 环境与开发约定
- Python 版本：`>=3.7`（见 `pyproject.toml`）。
- 建议在仓库根目录开发，常用命令：
```bash
pip install -e .
python -c "from btutils import Backtest"
```
- 若使用 `uv`：
```bash
uv sync
uv run python -c "from btutils import Backtest"
```
- 代码风格：当前仓库未发现格式化/静态检查配置（如 `ruff`、`black`、`mypy`），提交前请至少保证改动可导入、示例可运行。

## 测试与验证
- 当前仓库未发现 `tests/` 目录或测试配置文件。
- 建议最小验证方式：
  - 安装后执行导入检查；
  - 对新增指标或绘图逻辑补充最小可复现示例，并在 PR 描述中记录输入与结果。

## 提交与发布边界
- 提交信息建议使用中文且带类型前缀：`feat:`、`fix:`、`refactor:`、`docs:`、`test:`、`chore:`。
- 不要提交本地环境与敏感配置：`.env`、`venv/`、`.DS_Store` 已在 `.gitignore` 中。
- 当前仓库未发现部署脚本或 CI 配置；发布流程请以包管理平台实际流程为准。
