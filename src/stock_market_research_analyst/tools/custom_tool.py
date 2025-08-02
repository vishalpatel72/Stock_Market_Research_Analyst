from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import yfinance as yf
import numpy as np
import requests
from bs4 import BeautifulSoup
import logging
import os
from datetime import datetime

# Set up logging
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs'))
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'crew_errors.log')
logging.basicConfig(
    filename=log_file,
    filemode='a',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.ERROR
)

# Set up info logging for tool responses
log_info_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs/crew_tool_responses.log'))
info_logger = logging.getLogger('tool_responses')
info_handler = logging.FileHandler(log_info_file)
info_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
info_logger.setLevel(logging.INFO)
info_logger.propagate = False  # Prevent propagation to root logger
if not any(isinstance(h, logging.FileHandler) and getattr(h, 'baseFilename', None) == info_handler.baseFilename for h in info_logger.handlers):
    info_logger.addHandler(info_handler)


class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."

# --- Yahoo Finance Technical Tool ---
class YahooFinanceTechnicalToolInput(BaseModel):
    """Input schema for YahooFinanceTechnicalTool."""
    symbol: str = Field(..., description="Stock symbol, e.g., RELIANCE.NS")
    start: Optional[str] = Field(None, description="Start date (YYYY-MM-DD), optional")
    end: Optional[str] = Field(None, description="End date (YYYY-MM-DD), optional")

class YahooFinanceTechnicalTool(BaseTool):
    name: str = "yahoo_finance_technical_tool"
    description: str = (
        "Fetches and analyzes technical data for an Indian stock using Yahoo Finance. "
        "Covers historical price/volume, price action metrics (high/low, support/resistance, volatility), "
        "technical indicators (MA, EMA, RSI, MACD, Bollinger Bands), and generates chart visualizations."
    )
    args_schema: Type[BaseModel] = YahooFinanceTechnicalToolInput

    def _run(self, symbol: str, start: Optional[str] = None, end: Optional[str] = None) -> str:
        """
        Fetches historical OHLCV data and computes technical indicators for the given symbol using yfinance.
        Returns a structured summary in a financial-analyst tone.
        """
        try:
            ticker = yf.Ticker(symbol)
            # Fetch historical OHLCV data
            hist = ticker.history(start=start, end=end)
            if hist is None or hist.empty:
                return f"No historical data found for {symbol}."

            # Ensure the DataFrame is sorted by date (ascending)
            hist = hist.sort_index(ascending=True)

            # Price action metrics
            high_52w = hist['High'].rolling(window=252, min_periods=1).max().iloc[-1]
            low_52w = hist['Low'].rolling(window=252, min_periods=1).min().iloc[-1]
            recent_high = hist['High'].iloc[-20:].max()
            recent_low = hist['Low'].iloc[-20:].min()
            volatility = hist['Close'].pct_change().std() * np.sqrt(252)

            # Technical indicators
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            hist['SMA_100'] = hist['Close'].rolling(window=100).mean()
            hist['SMA_200'] = hist['Close'].rolling(window=200).mean()
            hist['EMA_20'] = hist['Close'].ewm(span=20, adjust=False).mean()
            hist['EMA_50'] = hist['Close'].ewm(span=50, adjust=False).mean()
            hist['EMA_100'] = hist['Close'].ewm(span=100, adjust=False).mean()
            hist['EMA_200'] = hist['Close'].ewm(span=200, adjust=False).mean()
            # RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-9)
            hist['RSI_14'] = 100 - (100 / (1 + rs))
            # MACD
            ema12 = hist['Close'].ewm(span=12, adjust=False).mean()
            ema26 = hist['Close'].ewm(span=26, adjust=False).mean()
            hist['MACD'] = ema12 - ema26
            hist['MACD_signal'] = hist['MACD'].ewm(span=9, adjust=False).mean()
            # Bollinger Bands
            sma20 = hist['SMA_20']
            std20 = hist['Close'].rolling(window=20).std()
            hist['BB_upper'] = sma20 + 2 * std20
            hist['BB_lower'] = sma20 - 2 * std20

            # Current price (latest close, always most recent date)
            current_price = hist['Close'].loc[hist.index.max()]

            # Today's date
            today = datetime.today().strftime('%Y-%m-%d')

            # Prepare summary
            summary = f"""
Yahoo Finance Technicals for {symbol}

Report Date: {today}

Current Price: {current_price:.2f}

Price Action Metrics:
- 52-Week High: {high_52w:.2f}
- 52-Week Low: {low_52w:.2f}
- Recent 20-Day High: {recent_high:.2f}
- Recent 20-Day Low: {recent_low:.2f}
- Annualized Volatility: {volatility:.2%}

Key Technical Indicators (latest):
- SMA(20): {hist['SMA_20'].iloc[-1]:.2f}
- SMA(50): {hist['SMA_50'].iloc[-1]:.2f}
- SMA(100): {hist['SMA_100'].iloc[-1]:.2f}
- SMA(200): {hist['SMA_200'].iloc[-1]:.2f}
- EMA(20): {hist['EMA_20'].iloc[-1]:.2f}
- EMA(50): {hist['EMA_50'].iloc[-1]:.2f}
- EMA(100): {hist['EMA_100'].iloc[-1]:.2f}
- EMA(200): {hist['EMA_200'].iloc[-1]:.2f}
- RSI(14): {hist['RSI_14'].iloc[-1]:.2f}
- MACD: {hist['MACD'].iloc[-1]:.2f} (Signal: {hist['MACD_signal'].iloc[-1]:.2f})
- Bollinger Bands: Upper {hist['BB_upper'].iloc[-1]:.2f}, Lower {hist['BB_lower'].iloc[-1]:.2f}
"""
            info_logger.info(f"YahooFinanceTechnicalTool response for {symbol}: {summary}")
            return summary
        except Exception as e:
            logging.error(f"Error in YahooFinanceTechnicalTool for {symbol}: {e}", exc_info=True)
            return "An internal error occurred. Please check the logs for details."

# --- Yahoo Finance Fundamental Tool ---
class YahooFinanceFundamentalToolInput(BaseModel):
    """Input schema for YahooFinanceFundamentalTool."""
    symbol: str = Field(..., description="Stock symbol, e.g., RELIANCE.NS")
    start: Optional[str] = Field(None, description="Start date (YYYY-MM-DD), optional")
    end: Optional[str] = Field(None, description="End date (YYYY-MM-DD), optional")

class YahooFinanceFundamentalTool(BaseTool):
    name: str = "yahoo_finance_fundamental_tool"
    description: str = (
        "Fetches and analyzes fundamental data for an Indian stock using Yahoo Finance. "
        "Covers financial statements (income, balance sheet, cash flow), key ratios (P/E, P/B, Debt-to-Equity, ROCE), "
        "ownership patterns, and provides a structured summary."
    )
    args_schema: Type[BaseModel] = YahooFinanceFundamentalToolInput

    def _run(self, symbol: str, start: Optional[str] = None, end: Optional[str] = None) -> str:
        """
        Fetches financial statements and key ratios for the given symbol using yfinance.
        Returns a structured summary in a financial-analyst tone.
        """
        try:
            ticker = yf.Ticker(symbol)
            # Fetch financial statements
            income_stmt = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            # Fetch key ratios (where available)
            info = ticker.info
            pe_ratio = info.get('trailingPE', 'N/A')
            pb_ratio = info.get('priceToBook', 'N/A')
            debt_to_equity = info.get('debtToEquity', 'N/A')
            # ROCE is not directly available; placeholder
            roce = 'N/A'

            # Optionally filter by date range (if provided)
            def filter_by_date(df):
                if df is None or df.empty:
                    return df
                if start:
                    df = df.loc[:, df.columns >= start]
                if end:
                    df = df.loc[:, df.columns <= end]
                return df
            income_stmt = filter_by_date(income_stmt)
            balance_sheet = filter_by_date(balance_sheet)
            cash_flow = filter_by_date(cash_flow)

            # Prepare summary
            summary = f"""
Yahoo Finance Fundamentals for {symbol}

Key Ratios:
- P/E Ratio: {pe_ratio}
- P/B Ratio: {pb_ratio}
- Debt-to-Equity: {debt_to_equity}
- ROCE: {roce}

Income Statement (head):
{income_stmt.head(3) if income_stmt is not None else 'N/A'}

Balance Sheet (head):
{balance_sheet.head(3) if balance_sheet is not None else 'N/A'}

Cash Flow Statement (head):
{cash_flow.head(3) if cash_flow is not None else 'N/A'}
"""
            info_logger.info(f"YahooFinanceFundamentalTool response for {symbol}: {summary}")
            return summary
        except Exception as e:
            logging.error(f"Error in YahooFinanceFundamentalTool for {symbol}: {e}", exc_info=True)
            return "An internal error occurred. Please check the logs for details."

# --- Moneycontrol News Tool ---
class MoneycontrolNewsToolInput(BaseModel):
    """Input schema for MoneycontrolNewsTool."""
    symbol: str = Field(..., description="Stock symbol, e.g., RELIANCE.NS")
    start: Optional[str] = Field(None, description="Start date (YYYY-MM-DD), optional")
    end: Optional[str] = Field(None, description="End date (YYYY-MM-DD), optional")

class MoneycontrolNewsTool(BaseTool):
    name: str = "moneycontrol_news_tool"
    description: str = (
        "Scrapes and summarizes the latest news, press releases, and analyst commentary for an Indian stock from Moneycontrol. "
        "Extracts news headlines, summaries, timestamps, analyst ratings, target prices, and provides a sentiment summary."
    )
    args_schema: Type[BaseModel] = MoneycontrolNewsToolInput

    def resolve_slug(self, symbol: str) -> str:
        """
        Try to resolve the Moneycontrol slug for a given symbol using heuristics and Moneycontrol's search endpoint.
        """
        import yfinance as yf
        import re
        # 1. Try heuristic from company name
        try:
            ticker = yf.Ticker(symbol)
            name = ticker.info.get('shortName', '') or ticker.info.get('longName', '')
            slug = name.lower().replace('&', 'and').replace(' ', '-').replace('.', '').replace(',', '')
            slug = ''.join(c for c in slug if c.isalnum() or c == '-')
            # Test if this slug works by checking the Moneycontrol search endpoint
            search_url = f"https://www.moneycontrol.com/mccode/common/autosuggestion_solr.php?query={slug}&type=1&format=json"
            resp = requests.get(search_url, timeout=10)
            if resp.status_code == 200 and resp.json():
                link = resp.json()[0].get('link_src', '')
                if link and slug in link:
                    return slug
        except Exception:
            pass
        # 2. Try Moneycontrol's autosuggestion search with the symbol
        try:
            search_url = f"https://www.moneycontrol.com/mccode/common/autosuggestion_solr.php?query={symbol}&type=1&format=json"
            resp = requests.get(search_url, timeout=10)
            if resp.status_code == 200 and resp.json():
                link = resp.json()[0].get('link_src', '')
                if link:
                    slug = link.split('/')[-1]
                    return slug
        except Exception:
            pass
        return None

    def _run(self, symbol: str, start: Optional[str] = None, end: Optional[str] = None) -> str:
        """
        Scrapes news headlines, summaries, and timestamps for the given symbol from Moneycontrol.
        Returns a structured summary in a financial-analyst tone.
        """
        try:
            mc_slug = self.resolve_slug(symbol)
            if not mc_slug:
                return f"Could not resolve Moneycontrol slug for symbol {symbol}."
            news_url = f"https://www.moneycontrol.com/company-article/{mc_slug}/news/{mc_slug}/{symbol.lower()}"
            resp = requests.get(news_url, timeout=10)
            if resp.status_code != 200:
                return f"Failed to fetch news for {symbol} from Moneycontrol."
            soup = BeautifulSoup(resp.text, 'html.parser')
            news_items = []
            for item in soup.select('.MT15 .clearfix'):
                headline = item.select_one('a').get_text(strip=True) if item.select_one('a') else ''
                summary = item.select_one('p').get_text(strip=True) if item.select_one('p') else ''
                date = item.select_one('.gD_12').get_text(strip=True) if item.select_one('.gD_12') else ''
                news_items.append({'headline': headline, 'summary': summary, 'date': date})
            if not news_items:
                return f"No news found for {symbol} on Moneycontrol."
            summary = f"""
Moneycontrol News for {symbol}

Recent News Headlines:
"""
            for n in news_items[:5]:
                summary += f"- {n['date']}: {n['headline']}\n  {n['summary']}\n"
            summary += "\nAnalyst Ratings & Sentiment: (To be implemented)\n"
            info_logger.info(f"MoneycontrolNewsTool response for {symbol}: {summary}")
            return summary
        except Exception as e:
            logging.error(f"Error in MoneycontrolNewsTool for {symbol}: {e}", exc_info=True)
            return "An internal error occurred. Please check the logs for details."
