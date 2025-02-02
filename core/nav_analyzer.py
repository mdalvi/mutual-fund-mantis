#!/usr/bin/env python3
import logging
# import random
# import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd
import quantstats as qs
import requests
from tenacity import retry, stop_after_attempt, wait_random

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NAVAnalyzer:
    """
    Class to analyze NAV data for mutual funds and generate reports
    """

    def __init__(self, csv_path: str, csrf_token: str):
        """
        Initialize NAV Analyzer

        :param csv_path: Path to input CSV file containing ISIN data
        :param csrf_token: CSRF token for API authentication
        """
        self.csv_path = csv_path
        self.csrf_token = csrf_token
        self.headers = {
            "sec-ch-ua-platform": "Linux",
            "X-CSRFToken": csrf_token,
            "Referer": "https://coin.zerodha.com/",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Brave";v="132"',
            "sec-ch-ua-mobile": "?0",
        }
        self.report_dir = Path("reports")
        self.report_dir.mkdir(exist_ok=True)

    def load_isin_data(self) -> pd.DataFrame:
        """
        Load ISIN data from CSV file

        :return: DataFrame containing ISIN data
        """
        try:
            df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(df)} records from {self.csv_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=2))
    def fetch_nav_data(self, isin: str) -> Dict:
        """
        Fetch NAV data for given ISIN with retry logic

        :param isin: ISIN code of the security
        :return: JSON response containing NAV data
        """
        url = f"https://staticassets.zerodha.com/coin/historical-nav/{isin}.json"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        data = response.json()
        if not data.get("status") == "success" or "data" not in data:
            raise ValueError(f"Invalid response format for ISIN {isin}")

        return data

    def process_nav_data(self, nav_data: List[List]) -> pd.Series:
        """
        Process NAV data into time series

        :param nav_data: List of [timestamp, nav_value] pairs
        :return: Series with DateTimeIndex and NAV values
        """
        df = pd.DataFrame(nav_data, columns=["timestamp", "nav"])
        df["date"] = pd.to_datetime(df["timestamp"], unit="s")
        return pd.Series(df["nav"].values, index=df["date"])

    def generate_statistics(self, nav_series: pd.Series) -> Dict:
        """
        Generate statistical metrics from NAV series

        :param nav_series: Time series of NAV values
        :return: Dictionary of statistical metrics
        """
        stats = {
            "cagr": qs.stats.cagr(nav_series),
            "volatility": qs.stats.volatility(nav_series),
            "sharpe": qs.stats.sharpe(nav_series, rf=0.03),
            "sortino": qs.stats.sortino(nav_series, rf=0.03),
            "max_drawdown": qs.stats.max_drawdown(nav_series),
            "value_at_risk": qs.stats.value_at_risk(nav_series),
        }
        return stats

    def generate_html_report(
            self, nav_series: pd.Series, security_info: pd.Series, isin: str
    ):
        """
        Generate HTML report using quantstats

        :param nav_series: Time series of NAV values
        :param security_info: Series containing security information
        :param isin: ISIN code of the security
        """
        report_path = self.report_dir / f"{isin}_report.html"
        qs.reports.html(
            nav_series,
            title=f"{security_info['security_name']} Analysis",
            output=str(report_path),
        )

    def analyze_securities(self):
        """
        Main method to analyze all securities and generate reports
        """
        df = self.load_isin_data()
        results = []

        for _, row in df.iterrows():
            try:
                logger.info(f"Processing ISIN: {row['isin']}")

                nav_data = self.fetch_nav_data(row["isin"])
                nav_series = self.process_nav_data(nav_data["data"])
                stats = self.generate_statistics(nav_series)

                # Generate HTML report
                self.generate_html_report(nav_series, row, row["isin"])

                # Add stats to results
                result_row = row.to_dict()
                result_row.update(stats)
                results.append(result_row)

                # Random sleep to avoid throttling
                # time.sleep(random.uniform(1, 2))

            except Exception as e:
                logger.error(
                    f"Error processing ISIN {row['isin']}: {str(e)}", exc_info=True
                )
                continue

        # Save consolidated report
        report_df = pd.DataFrame(results)
        report_date = datetime.now().strftime("%Y-%m-%d")
        report_df.to_csv(self.report_dir / f"{report_date}_report.csv", index=False)
        logger.info("Analysis completed")
