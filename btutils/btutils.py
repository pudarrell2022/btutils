import pandas as _pd
import numpy as _np
import matplotlib.pyplot as _plt
import seaborn as _sns
from scipy.stats import norm as _norm, linregress as _linregress


COLOR_SCHEME = {
    "strategy": "#1f77b4",
    "benchmark": "#ff7f0e",
    "excess": "#d62728",
    "drawdown": "#2ca02c",
    "grid": "#cccccc",
    "text": "#333333",
    "background": "#ffffff",
    "spine": "#000000",
}
PLOT_STYLE = {
    "figure": {
        "dpi": 100,
        "facecolor": COLOR_SCHEME["background"],
        "figsize": (12, 6),
    },
    "title": {
        "fontname": "Arial",
        "fontsize": 14,
        "fontweight": "bold",
        "color": COLOR_SCHEME["text"],
        "y": 0.95,
    },
    "legend": {
        "upper_left": {
            "loc": "upper left",
            "frameon": True,
            "fontsize": 10,
            "labelspacing": 0.5,
            "handlelength": 1.5,
            "handleheight": 1.0,
        },
        "lower_left": {
            "loc": "lower left",
            "frameon": True,
            "fontsize": 10,
            "labelspacing": 0.5,
            "handlelength": 1.5,
            "handleheight": 1.0,
        },
    },
    "spine": {
        "linewidth": 0.5,
        "alpha": 1,
        "linestyle": "-",
        "color": COLOR_SCHEME["spine"],
        "visible": {"top": False, "right": False, "bottom": True, "left": True},
    },
    "tick": {
        "pad": 2,
        "colors": COLOR_SCHEME["text"],
        "labelsize": 10,
        "direction": "out",
        "length": 4,
        "width": 0.5,
    },
    "ticklabel": {
        "x": {
            "fontname": "Arial",
            "fontsize": 10,
            "fontweight": "normal",
            "color": COLOR_SCHEME["text"],
            "rotation": 45,
            "ha": "right",
        },
        "y": {
            "fontname": "Arial",
            "fontsize": 10,
            "fontweight": "normal",
            "color": COLOR_SCHEME["text"],
            "rotation": 0,
            "ha": "right",
        },
    },
    "axis": {
        "formatter": {
            "pct0": lambda x, p: f"{x:.0%}",
            "pct2": lambda x, p: f"{x:.2%}",
            "float": lambda x, p: f"{x:.2f}",
            "int": lambda x, p: f"{int(x)}",
        },
    },
    "axislabel": {
        "fontname": "Arial",
        "fontsize": 12,
        "fontweight": "bold",
        "color": COLOR_SCHEME["text"],
        "labelpad": 20,
    },
    "grid": {
        "both": {
            "linestyle": "--",
            "alpha": 0.5,
            "color": COLOR_SCHEME["grid"],
            "axis": "both",
            "which": "major",
        },
        "y": {
            "linestyle": "--",
            "alpha": 0.5,
            "color": COLOR_SCHEME["grid"],
            "axis": "y",
            "which": "major",
        },
    },
    "layout": {"pad": 2.0, "h_pad": 0, "w_pad": 0},
}


def save_figure(fig, filename, dpi=300):
    fig.savefig(
        filename,
        dpi=dpi,
        bbox_inches="tight",
        pad_inches=0.1,
        facecolor=COLOR_SCHEME["background"],
    )


def get_positions(dt_series, freq="D"):
    df = dt_series.rename_axis("datetime").reset_index()

    if freq == "YE":
        df["year"] = df["datetime"].dt.strftime("%Y")
        year_points = df.groupby("year")["datetime"].first().dropna()

        total_years = len(year_points)
        step = max(1, total_years // 5)

        positions = year_points[::step]
        labels = [d.strftime("%Y") for d in positions]

        return positions, labels

    df["ym"] = df["datetime"].dt.strftime("%Y%m")
    df["year"] = df["datetime"].dt.strftime("%Y")

    month_points = df.groupby("ym")["datetime"].first().dropna()
    year_points = df.groupby("year")["datetime"].first().dropna()

    total_months = len(month_points)
    month_step = max(1, total_months // 5)

    if month_step >= 12:
        year_step = max(1, len(year_points) // 5)
        positions = year_points[::year_step]
        labels = [d.strftime("%Y") for d in positions]
    else:
        positions = month_points[::month_step]
        labels = [d.strftime("%Y%m") for d in positions]

    return positions, labels


class Stats:
    def __init__(self, parent=None):
        self.parent = parent
        self.data = parent.data

    def cumulative_return(self, absolute=True):
        if absolute:
            res = (1 + self.data).prod()
        else:
            res = (1 + self.data).prod() - 1
        return res

    def annual_return(self, compounded=True):
        years = len(self.data) / 252
        if compounded:
            res = self.cumulative_return() ** (1 / years) - 1
        else:
            res = self.data.mean() * 252
        return res

    def annual_volatility(self):
        return self.data.std() * _np.sqrt(252)

    def sharpe_ratio(self, rf=0.0):
        return (self.annual_return() - rf) / self.annual_volatility()

    def sortino_ratio(self, rf=0.0):
        return (self.annual_return() - rf) / (
            self.data[self.data < 0].std() * _np.sqrt(252)
        )

    def beta(self, index):
        index = index.loc[index.index.isin(self.parent.index)]
        return self.parent.cov(index) / index.var()

    def alpha(self, index):
        index = index.loc[index.index.isin(self.parent.index)]
        return self.parent.annual_return() - self.beta(index) * index.annual_return()

    def max_drawdown(self):
        res = self.parent.to_drawdown().min()
        return res

    def longest_drawdown(self):
        res = self.parent.to_drawdown()
        res = res[res == 0].index.diff().max().days
        return res

    def win_rate(self):
        res = (self.data > 0).sum() / (self.data != 0).sum()
        return res

    def avg_win(self):
        res = self.data[self.data > 0].mean()
        return res

    def avg_loss(self):
        res = self.data[self.data < 0].mean()
        return res

    def avg_return(self):
        res = self.data
        res = res[res != 0].dropna().mean()
        return res

    def payoff_rate(self):
        res = self.avg_win() / -self.avg_loss()
        return res

    def time_in_market(self):
        res = (self.data != 0).sum() / len(self.data)
        return res

    def skew(self):
        res = self.data.skew()
        return res

    def kurtosis(self):
        res = self.data.kurtosis()
        return res

    def var(self, confidence=0.95):
        mu = self.data.mean()
        sigma = self.data.std()
        return _norm.ppf(1 - confidence, mu, sigma)

    def cvar(self, confidence=0.95):
        var = self.var(confidence)
        cvar = self.data[self.data <= var].mean()
        return cvar if not _np.isnan(cvar) else 0

    def r2(self, benchmark):
        benchmark = benchmark.loc[benchmark.index.isin(self.parent.index)]
        _, _, r, _, _ = _linregress(self.data, benchmark)
        return r**2

    def best(self, freq="D", num=1, compounded=True):
        res = self.parent.to_return(freq, compounded)
        res = res.reset_index()
        res.columns = ["datetime", "return"]
        res = res.sort_values(by="return", ascending=False)
        res = res.head(num).reset_index(drop=True)
        return res

    def worst(self, freq="D", num=1, compounded=True):
        res = self.parent.to_return(freq, compounded)
        res = res.reset_index()
        res.columns = ["datetime", "return"]
        res = res.sort_values(by="return", ascending=True)
        res = res.head(num).reset_index(drop=True)
        return res


class Plots:
    def __init__(self, parent=None):
        self.parent = parent
        self.data = parent.data

    def line(
        self,
        cummulative=True,
        benchmark=None,
        show_drawdown=False,
        show_excess=False,
        worst_num=0,
        save_fig=None,
        ymean=False,
        y0=False,
        yformat="pct0",
    ):
        if cummulative:
            res = self.parent.to_cumulative_return()
        else:
            res = self.parent

        # Create Figure
        if show_drawdown:
            fig, axes = _plt.subplots(
                2,
                1,
                figsize=PLOT_STYLE["figure"]["figsize"],
                dpi=PLOT_STYLE["figure"]["dpi"],
                sharex=True,
                gridspec_kw={"height_ratios": [3, 1], "hspace": 0},
            )
        else:
            fig, axes = _plt.subplots(
                figsize=PLOT_STYLE["figure"]["figsize"], dpi=PLOT_STYLE["figure"]["dpi"]
            )
            axes = _np.array([axes])
        fig.set_facecolor(PLOT_STYLE["figure"]["facecolor"])
        fig.suptitle("Returns Line Chart", **PLOT_STYLE["title"])

        # Plot
        _sns.lineplot(
            data=res,
            ax=axes[0],
            label="Strategy",
            color=COLOR_SCHEME["strategy"],
            alpha=0.8,
        )
        if benchmark is not None:
            if cummulative:
                benchmark = benchmark.to_cumulative_return()
            else:
                benchmark = benchmark
            _sns.lineplot(
                data=benchmark,
                ax=axes[0],
                label="Benchmark",
                color=COLOR_SCHEME["benchmark"],
                alpha=0.8,
            )
        if show_excess:
            excess = res - benchmark
            axes[0].fill_between(
                excess.index,
                excess,
                0,
                color=COLOR_SCHEME["excess"],
                alpha=0.25,
                label="Excess",
            )
        if show_drawdown:
            dd = self.parent.to_drawdown()
            _sns.lineplot(
                data=dd,
                ax=axes[1],
                label="Drawdown",
                color=COLOR_SCHEME["drawdown"],
                alpha=0.8,
            )
            axes[1].fill_between(
                dd.index, dd, 0, color=COLOR_SCHEME["drawdown"], alpha=0.25
            )
            axes[1].legend(**PLOT_STYLE["legend"]["lower_left"])
        if worst_num > 0:
            dd_df = self.parent.get_worst_period(num=worst_num)
            dd_df.apply(
                lambda row: axes[0].axvspan(
                    row["start_date"],
                    row["end_date"],
                    color=COLOR_SCHEME["drawdown"],
                    alpha=0.1,
                ),
                axis=1,
            )
        if ymean:
            axes[0].axhline(
                res.mean(),
                ls="--",
                lw=0.8,
                color=COLOR_SCHEME["strategy"],
                zorder=2,
                alpha=0.5,
                label="Strategy Mean",
            )
            if benchmark is not None:
                axes[0].axhline(
                    benchmark.mean(),
                    ls="--",
                    lw=0.8,
                    color=COLOR_SCHEME["benchmark"],
                    zorder=2,
                    alpha=0.5,
                    label="Benchmark Mean",
                )
        if y0:
            axes[0].axhline(0, ls="-", lw=0.8, color="#000000", zorder=2, alpha=1)
        axes[0].legend(**PLOT_STYLE["legend"]["upper_left"])

        # Adjust Axes Style
        for i, ax in enumerate(axes):
            ax.set_facecolor(PLOT_STYLE["figure"]["facecolor"])

            for spine_name, spine in ax.spines.items():
                spine.set_linewidth(PLOT_STYLE["spine"]["linewidth"])
                spine.set_alpha(PLOT_STYLE["spine"]["alpha"])
                spine.set_linestyle(PLOT_STYLE["spine"]["linestyle"])
                spine.set_color(PLOT_STYLE["spine"]["color"])
                spine.set_visible(PLOT_STYLE["spine"]["visible"].get(spine_name, True))
            positions, labels = get_positions(res, freq="D")
            if not (show_drawdown and i == 0):
                ax.set_xticks(positions)
                ax.tick_params(**PLOT_STYLE["tick"])
                ax.set_xticklabels(labels, **PLOT_STYLE["ticklabel"]["x"])
            ax.yaxis.set_major_formatter(
                _plt.FuncFormatter(PLOT_STYLE["axis"]["formatter"][yformat])
            )
            ax.yaxis.set_major_locator(_plt.MaxNLocator(5))
            ax.set_xlabel("Datetime", **PLOT_STYLE["axislabel"])
            if i == 0:
                ax.set_ylabel("Cumulative Returns", **PLOT_STYLE["axislabel"])
            elif i == 1:
                ax.set_ylabel("Drawdown", **PLOT_STYLE["axislabel"])
            ax.grid(**PLOT_STYLE["grid"]["both"])

        fig.tight_layout(**PLOT_STYLE["layout"])
        if save_fig is not None:
            save_figure(fig, save_fig)
        else:
            _plt.show()

    def bar(self, benchmark=None, freq="D", compounded=True, save_fig=None):
        # Calculate Daily Excess Returns
        if benchmark is not None:
            res = Backtest(self.parent - benchmark)
        else:
            res = self.parent
        res = res.to_return(freq, compounded)

        # Create Figure
        fig, ax = _plt.subplots(figsize=(12, 6))
        fig.set_facecolor(PLOT_STYLE["figure"]["facecolor"])
        ax.set_facecolor(PLOT_STYLE["figure"]["facecolor"])
        fig.suptitle(f"Returns Bar Chart ({freq})", **PLOT_STYLE["title"])

        # Plot
        colors = ["#2ecc71" if x <= 0 else "#e74c3c" for x in res]
        n_bars = len(res)
        fig_width = fig.get_figwidth() * fig.dpi
        bar_width = (fig_width * 0.8) / n_bars
        ax.bar(
            res.index,
            res.values,
            color=colors,
            width=bar_width,
            alpha=0.8,
            label="Strategy",
        )
        ax.axhline(0, ls="-", lw=0.8, color="#000000", zorder=2, alpha=1)
        if benchmark is not None:
            ax.axhline(
                benchmark.mean(),
                ls="--",
                lw=0.8,
                color=COLOR_SCHEME["benchmark"],
                zorder=2,
                alpha=0.5,
                label="Benchmark Mean",
            )
        ax.axhline(
            res.mean(),
            ls="--",
            lw=0.8,
            color=COLOR_SCHEME["strategy"],
            zorder=2,
            alpha=0.5,
            label="Strategy Mean",
        )
        ax.legend(**PLOT_STYLE["legend"]["upper_left"])

        # Adjust Axes Style
        for spine_name, spine in ax.spines.items():
            spine.set_linewidth(PLOT_STYLE["spine"]["linewidth"])
            spine.set_alpha(PLOT_STYLE["spine"]["alpha"])
            spine.set_linestyle(PLOT_STYLE["spine"]["linestyle"])
            spine.set_color(PLOT_STYLE["spine"]["color"])
            spine.set_visible(PLOT_STYLE["spine"]["visible"].get(spine_name, True))
        positions, labels = get_positions(res, freq)
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, **PLOT_STYLE["ticklabel"]["x"])
        ax.tick_params(**PLOT_STYLE["tick"])
        ax.yaxis.set_major_formatter(
            _plt.FuncFormatter(PLOT_STYLE["axis"]["formatter"]["pct0"])
        )
        ax.yaxis.set_major_locator(_plt.MaxNLocator(5))
        ax.set_xlabel("Datetime", **PLOT_STYLE["axislabel"])
        ax.set_ylabel("Returns", **PLOT_STYLE["axislabel"])
        ax.grid(**PLOT_STYLE["grid"]["y"])

        fig.tight_layout(**PLOT_STYLE["layout"])
        if save_fig is not None:
            save_figure(fig, save_fig)
        else:
            _plt.show()

    def hist(self, benchmark=None, freq="D", compounded=True, save_fig=None):
        # Calculate Daily Excess Returns
        if benchmark is not None:
            res = Backtest(self.parent - benchmark)
        else:
            res = self.parent
        res = res.to_return(freq, compounded)

        # Create Figure
        fig, ax = _plt.subplots(figsize=(12, 6))
        fig.set_facecolor(PLOT_STYLE["figure"]["facecolor"])
        ax.set_facecolor(PLOT_STYLE["figure"]["facecolor"])
        fig.suptitle(f"Returns Histogram ({freq})", **PLOT_STYLE["title"])

        # Plot
        n_bins = min(50, max(5, int(len(res) ** 0.5)))
        _sns.kdeplot(
            data=res,
            color=COLOR_SCHEME["strategy"],
            ax=ax,
            warn_singular=False,
            label="KDE",
        )
        _sns.histplot(
            data=res,
            bins=n_bins,
            alpha=0.8,
            kde=False,
            stat="density",
            color=COLOR_SCHEME["strategy"],
            ax=ax,
            label="Strategy",
        )
        ax.axvline(
            res.mean(), ls="--", lw=2, color="red", zorder=2, alpha=0.5, label="Mean"
        )
        ax.legend(**PLOT_STYLE["legend"]["upper_left"])

        # Adjust Axes Style
        for spine_name, spine in ax.spines.items():
            spine.set_linewidth(PLOT_STYLE["spine"]["linewidth"])
            spine.set_alpha(PLOT_STYLE["spine"]["alpha"])
            spine.set_linestyle(PLOT_STYLE["spine"]["linestyle"])
            spine.set_color(PLOT_STYLE["spine"]["color"])
            spine.set_visible(PLOT_STYLE["spine"]["visible"].get(spine_name, True))

        ax.xaxis.set_major_formatter(
            _plt.FuncFormatter(PLOT_STYLE["axis"]["formatter"]["pct2"])
        )
        ax.yaxis.set_major_locator(_plt.MaxNLocator(5))
        ax.tick_params(**PLOT_STYLE["tick"])
        ax.set_xlabel("Returns", **PLOT_STYLE["axislabel"])
        ax.set_ylabel("Count", **PLOT_STYLE["axislabel"])
        ax.grid(**PLOT_STYLE["grid"]["y"])

        fig.tight_layout(**PLOT_STYLE["layout"])
        if save_fig is not None:
            save_figure(fig, save_fig)
        else:
            _plt.show()

    def dist(self, benchmark=None, save_fig=None):
        # Calculate Daily Excess Returns
        if benchmark is not None:
            res = Backtest(self.parent - benchmark)
        else:
            res = self.parent
        res_df = _pd.DataFrame(
            {
                "Day": res.to_return("D"),
                "Week": res.to_return("WE"),
                "Month": res.to_return("ME"),
                "Quarter": res.to_return("QE"),
                "Year": res.to_return("YE"),
            }
        )

        # Create Figure
        fig, ax = _plt.subplots(figsize=(12, 6))
        fig.set_facecolor(PLOT_STYLE["figure"]["facecolor"])
        ax.set_facecolor(PLOT_STYLE["figure"]["facecolor"])
        fig.suptitle("Returns Distribution", **PLOT_STYLE["title"])

        # Plot
        _sns.boxplot(
            data=res_df,
            ax=ax,
            palette={
                "Day": "#FEDD78",
                "Week": "#348DC1",
                "Month": "#BA516B",
                "Quarter": "#4FA487",
                "Year": "#9B59B6",
            },
        )

        # Adjust Axes Style
        for spine_name, spine in ax.spines.items():
            spine.set_linewidth(PLOT_STYLE["spine"]["linewidth"])
            spine.set_alpha(PLOT_STYLE["spine"]["alpha"])
            spine.set_linestyle(PLOT_STYLE["spine"]["linestyle"])
            spine.set_color(PLOT_STYLE["spine"]["color"])
            spine.set_visible(PLOT_STYLE["spine"]["visible"].get(spine_name, True))
        ax.tick_params(**PLOT_STYLE["tick"])
        ax.yaxis.set_major_formatter(
            _plt.FuncFormatter(PLOT_STYLE["axis"]["formatter"]["pct0"])
        )
        ax.set_xlabel("Frequency", **PLOT_STYLE["axislabel"])
        ax.set_ylabel("Returns", **PLOT_STYLE["axislabel"])
        ax.grid(**PLOT_STYLE["grid"]["y"])

        fig.tight_layout(**PLOT_STYLE["layout"])
        if save_fig is not None:
            save_figure(fig, save_fig)
        else:
            _plt.show()

    def heatmap(
        self,
        benchmark=None,
        freq="ME",
        compounded=True,
        save_fig=None,
    ):
        annot = False if freq == "WE" else True
        # Calculate Daily Relative Returns
        if benchmark is not None:
            res = Backtest(self.parent - benchmark)
        else:
            res = self.parent
        value = res.name
        res = res.to_return(freq, compounded).to_frame()
        res["index"] = res.index.strftime("%Y")
        if freq == "WE":
            res["col"] = res.index.strftime("%W")
            name = "Week"
        elif freq == "ME":
            res["col"] = res.index.strftime("%m")
            name = "Month"
        elif freq == "QE":
            res["col"] = res.index.quarter
            name = "Quarter"
        else:
            pass
        res = res.pivot(index="index", columns="col", values=value).fillna(0)

        # Create Figure
        fig, ax = _plt.subplots(figsize=(12, 6))
        fig.set_facecolor(PLOT_STYLE["figure"]["facecolor"])
        ax.set_facecolor(PLOT_STYLE["figure"]["facecolor"])
        fig.suptitle(f"Returns Heatmap ({freq})", **PLOT_STYLE["title"])

        # Plot
        _sns.heatmap(
            res,
            ax=ax,
            annot=annot,
            center=0,
            annot_kws={"size": 10},
            fmt="0.2%",
            linewidths=0.5,
            cbar=True,
            cmap="RdYlGn_r",
            cbar_kws={"format": _plt.FuncFormatter(lambda x, p: f"{x:.2%}")},
        )

        # Adjust Axes Style
        for spine_name, spine in ax.spines.items():
            spine.set_linewidth(PLOT_STYLE["spine"]["linewidth"])
            spine.set_alpha(PLOT_STYLE["spine"]["alpha"])
            spine.set_linestyle(PLOT_STYLE["spine"]["linestyle"])
            spine.set_color(PLOT_STYLE["spine"]["color"])
            spine.set_visible(PLOT_STYLE["spine"]["visible"].get(spine_name, True))
        ax.tick_params(**PLOT_STYLE["tick"])
        ax.set_yticklabels(res.index, **PLOT_STYLE["ticklabel"]["y"])
        ax.set_xlabel(name, **PLOT_STYLE["axislabel"])
        ax.set_ylabel("Year", **PLOT_STYLE["axislabel"])

        fig.tight_layout(**PLOT_STYLE["layout"])
        if save_fig is not None:
            save_figure(fig, save_fig)
        else:
            _plt.show()

    def rolling_volatility(self, benchmark=None, freq="D", window=60, save_fig=None):
        res = self.parent.to_rolling_volatility(freq, window)
        if benchmark is not None:
            benchmark = benchmark.to_rolling_volatility(freq, window)
            res.plots.line(
                benchmark=benchmark,
                save_fig=save_fig,
                cummulative=False,
                ymean=True,
                yformat="pct0",
            )
        else:
            res.plots.line(
                save_fig=save_fig, cummulative=False, ymean=True, yformat="pct0"
            )

    def rolling_sharpe(
        self, benchmark=None, freq="D", window=60, rf=0.015, save_fig=None
    ):
        res = self.parent.to_rolling_sharpe(freq, window, rf)
        if benchmark is not None:
            benchmark = benchmark.to_rolling_sharpe(freq, window, rf)
            res.plots.line(
                benchmark=benchmark,
                save_fig=save_fig,
                cummulative=False,
                ymean=True,
                yformat="float",
            )
        else:
            res.plots.line(
                save_fig=save_fig,
                cummulative=False,
                ymean=True,
                y0=True,
                yformat="float",
            )

    def rolling_sortino(
        self, benchmark=None, freq="D", window=60, rf=0.015, save_fig=None
    ):
        res = self.parent.to_rolling_sortino(freq, window, rf)
        if benchmark is not None:
            benchmark = benchmark.to_rolling_sortino(freq, window, rf)
            res.plots.line(
                benchmark=benchmark,
                save_fig=save_fig,
                cummulative=False,
                ymean=True,
                yformat="float",
            )
        else:
            res.plots.line(
                save_fig=save_fig,
                cummulative=False,
                ymean=True,
                y0=True,
                yformat="float",
            )

    def rolling_beta(self, index, freq="D", window=60, save_fig=None):
        res = self.parent.to_rolling_beta(index, freq, window)
        res.plots.line(
            save_fig=save_fig, cummulative=False, ymean=True, y0=True, yformat="float"
        )

    def rolling_alpha(self, index, freq="D", window=60, save_fig=None):
        res = self.parent.to_rolling_alpha(index, freq, window)
        res.plots.line(
            save_fig=save_fig, cummulative=False, ymean=True, y0=True, yformat="float"
        )


class Backtest(_pd.Series):
    def __init__(self, data, name=None):
        super().__init__(data)
        self.name = name if name is not None else "Strategy"
        self.start_date = data.index.min()
        self.end_date = data.index.max()
        self.data = data
        self.stats = Stats(self)
        self.plots = Plots(self)

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

    def slice_date(self, start_date, end_date=None):
        if end_date is None:
            end_date = self.end_date
        if start_date == "mtd":
            start_date = self.start_date.replace(day=1)
        elif start_date == "qtd":
            current_quarter = (self.start_date.month - 1) // 3
            start_date = self.start_date.replace(month=current_quarter * 3 + 1, day=1)
        elif start_date == "ytd":
            start_date = self.start_date.replace(month=1, day=1)
        return Backtest(self.data.loc[start_date:end_date], name=self.name)

    def to_return(self, freq="D", compounded=True, rf=0.0, rf_period=252):
        freq = "W" if freq == "WE" else freq
        rf = rf / rf_period
        if compounded:
            res = (
                (self.data - rf)
                .resample(freq)
                .apply(lambda x: None if x.isna().all() else (1 + x).prod() - 1)
                .dropna()
            )
        else:
            res = (self.data - rf).resample(freq).sum()
        return Backtest(res, name=self.name)

    def to_cumulative_return(self, absolute=True):
        if absolute:
            res = (1 + self.data.fillna(0)).cumprod()
        else:
            res = (1 + self.data.fillna(0)).cumprod() - 1
        return Backtest(res, name=self.name)

    def to_drawdown(self):
        res = self.to_cumulative_return().data
        res = res / res.cummax() - 1
        return Backtest(res, name=self.name)

    def to_rolling_volatility(self, freq="D", window=60):
        res = self.to_return(freq).data
        res = res.rolling(window).apply(lambda x: Backtest(x).stats.annual_volatility())
        return Backtest(res, name=self.name)

    def to_rolling_sharpe(self, freq="D", window=60, rf=0.015):
        res = self.to_return(freq).data
        res = res.rolling(window).apply(lambda x: Backtest(x).stats.sharpe_ratio(rf))
        return Backtest(res, name=self.name)

    def to_rolling_sortino(self, freq="D", window=60, rf=0.015):
        res = self.to_return(freq).data
        res = res.rolling(window).apply(lambda x: Backtest(x).stats.sortino_ratio(rf))
        return Backtest(res, name=self.name)

    def to_rolling_beta(self, index, freq="D", window=60):
        res = self.to_return(freq).data
        res = res.rolling(window).apply(lambda x: Backtest(x).stats.beta(index))
        return Backtest(res, name=self.name)

    def to_rolling_alpha(self, index, freq="D", window=60):
        res = self.to_return(freq).data
        res = res.rolling(window).apply(lambda x: Backtest(x).stats.alpha(index))
        return Backtest(res, name=self.name)

    def get_worst_period(self, num=1):
        res = self.to_drawdown().data
        df = res[res == 0].rename_axis("start_date").reset_index()[["start_date"]]
        df["end_date"] = df["start_date"].shift(-1)
        df = df.dropna()
        df["duration"] = (df["end_date"] - df["start_date"]).dt.days
        df["max_drawdown"] = df[["start_date", "end_date"]].apply(
            lambda row: res.loc[row["start_date"] : row["end_date"]].min(), axis=1
        )
        df = df.sort_values(by="duration", ascending=False)
        return df.head(num)

    def metrics(self, index_list=None, rf=0.0):
        if index_list is None:
            index_list = [
                "annual_return",
                "annual_volatility",
                "sharpe_ratio",
                "max_drawdown",
                "win_rate",
                "payoff_rate",
            ]
        res = {
            "Start Date": self.start_date.strftime("%Y-%m-%d"),
            "End Date": self.end_date.strftime("%Y-%m-%d"),
            "Time in Market %": f"{self.stats.time_in_market():.2%}",
        }
        for index in index_list:
            if index == "annual_return":
                res["Annual Return %"] = f"{self.stats.annual_return():.2%}"
            elif index == "annual_volatility":
                res["Annual Volatility %"] = f"{self.stats.annual_volatility():.2%}"
            elif index == "sharpe_ratio":
                res["Sharpe Ratio"] = f"{self.stats.sharpe_ratio(rf):.2f}"
            elif index == "max_drawdown":
                res["Max Drawdown %"] = f"{self.stats.max_drawdown():.2%}"
            elif index == "win_rate":
                res["Win Rate %"] = f"{self.stats.win_rate():.2%}"
            elif index == "payoff_rate":
                res["Payoff Rate"] = f"{self.stats.payoff_rate():.2%}"
            else:
                pass

        return _pd.Series(res)


if __name__ == "__main__":
    pass
