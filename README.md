# Mutual Fund Mantis 🦗

Mutual Fund Mantis is a Python tool for analyzing historical NAV (Net Asset Value) data of mutual funds. It fetches NAV time series data, generates statistical metrics, and creates HTML reports for each fund using the quantstats library.

## Features

* Load list of mutual funds to analyze from CSV file
* Fetch historical NAV data for each fund from a REST API
* Generate key stats like CAGR, volatility, Sharpe ratio, max drawdown etc.
* Create pretty HTML report with charts for each fund
* Output consolidated metrics for all funds analyzed to CSV

## Installation

1. Clone the repo:

```
git clone https://github.com/yourusername/mutual-fund-mantis.git
cd mutual-fund-mantis
```

2. This project uses Poetry for dependency management. Install dependencies with:

```
poetry install
```

3. The quantstats v0.0.64 package has a known resampling bug which needs a small fix. Modify core.py around line 292 as follows:

```
# core.py

if resample:
    returns = returns.resample(resample)
    returns = returns.last() if compound is True else returns.sum()
    if isinstance(benchmark, _pd.Series):
        benchmark = benchmark.resample(resample)  
        benchmark = benchmark.last() if compound is True else benchmark.sum()
```
More details: quantstats [Issue #376](https://github.com/ranaroussi/quantstats/issues/376)

## Usage

1. Prepare an input CSV file with the following columns:

* isin: ISIN code of the mutual fund
* security_name: Name of the fund

2. Run the analysis:

```
poetry run python main.py --csv_path path/to/input.csv --csrf_token YOUR_CSRF_TOKEN
```

The --csrf_token option should contain the CSRF token required for API authentication.

3. Analysis artifacts are stored in the reports/ directory:

* YYYY-MM-DD_report.csv: Consolidated metrics for all funds
* ISIN_report.html: Detailed report for each fund


## License

This project is open source and available under the MIT License.