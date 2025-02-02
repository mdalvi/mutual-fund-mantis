#!/usr/bin/env python3
import argparse
import logging

from core.nav_analyzer import NAVAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the script
    """
    parser = argparse.ArgumentParser(description="Analyze NAV data for mutual funds")
    parser.add_argument("--csv_path", help="Path to input CSV file")
    parser.add_argument("--csrf_token", help="CSRF token for API authentication")

    args = parser.parse_args()

    analyzer = NAVAnalyzer(args.csv_path, args.csrf_token)
    analyzer.analyze_securities()


if __name__ == "__main__":
    main()
