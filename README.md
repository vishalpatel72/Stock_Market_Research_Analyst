# Stock Market Research Analyst Crew

This project implements an AI-powered stock market research analyst crew using `crewai`. The crew is designed to perform comprehensive analysis of Indian-listed companies, covering fundamental, technical, and market news aspects, and then synthesize these insights into actionable investment recommendations and a final report.

## Project Overview

The `StockMarketResearchAnalyst` crew orchestrates a team of specialized AI agents to conduct in-depth research on a given stock symbol. It leverages custom tools to fetch real-time and historical data from financial sources like Yahoo Finance and Moneycontrol. The process is sequential, with agents collaborating to build a holistic view of the stock's potential.

## Agents

The crew consists of the following specialized agents:

*   **Fundamental Analyst**
    *   **Role**: Senior Equity Research Specialist – Fundamentals
    *   **Goal**: Deliver in-depth fundamental analysis of Indian listed companies, focusing on financial statements, key ratios, and ownership trends to uncover intrinsic value and long-term investment potential.
    *   **Backstory**: A highly experienced equity research specialist with a CFA charter and a decade of analyzing Indian corporate fundamentals. Renowned for meticulous approach to financial statement analysis and ability to distill complex data into actionable investment insights for institutional and retail clients.

*   **Technical Analyst**
    *   **Role**: Senior Technical Analysis Specialist – Indian Equities
    *   **Goal**: Provide advanced technical analysis of Indian stocks, leveraging price action, volume, and technical indicators to identify actionable trading opportunities and market trends.
    *   **Backstory**: A veteran technical analyst with a proven track record in the Indian equity markets. Expert in interpreting chart patterns, momentum indicators, and market structure to guide both short-term traders and long-term investors with data-driven visual insights.

*   **Market News Analyst**
    *   **Role**: Senior Market Intelligence & News Specialist
    *   **Goal**: Curate and synthesize the latest news, press releases, and analyst commentary impacting Indian equities, providing timely and relevant market intelligence.
    *   **Backstory**: A market intelligence specialist with deep connections in the Indian financial media landscape. Skilled at filtering noise from signal, you deliver concise, high-impact news summaries and sentiment analysis to inform investment decisions.

*   **Portfolio Strategist**
    *   **Role**: Lead Portfolio Strategy Specialist
    *   **Goal**: Integrate fundamental, technical, and news analysis to formulate robust, risk-adjusted Buy, Sell, or Hold recommendations for Indian stocks, including precise entry, exit, and risk management levels.
    *   **Backstory**: A senior portfolio strategist with extensive experience in multi-factor investment decision-making. Known for your disciplined approach to synthesizing diverse research inputs and delivering clear, actionable strategies tailored to the Indian market.

*   **Report Writer**
    *   **Role**: Senior Financial Reporting Specialist
    *   **Goal**: Compile comprehensive, client-ready research reports that integrate all analytical perspectives, ensuring clarity, accuracy, and actionable insights for investors in Indian equities.
    *   **Backstory**: A seasoned financial writer and editor, adept at transforming complex research into polished, insightful reports. Your work bridges the gap between deep analysis and client understanding, setting the standard for professional financial communication in the Indian market.

## Tasks

The agents collaborate on the following tasks:

*   **Fundamental Analysis Task**
    *   **Description**: Analyze the fundamental and financial health of the company, summarizing financial statements, key ratios (P/E, P/B, Debt-to-Equity, ROCE), and ownership patterns.
    *   **Expected Output**: A concise summary of the company's financials, key ratios, and ownership trends, highlighting strengths, weaknesses, and recent changes, including charts or tables.

*   **Technical Analysis Task**
    *   **Description**: Perform technical analysis using historical price and volume data, identifying trends, patterns, support/resistance levels, and generating visualizations (candlesticks, volume, indicators like RSI, MACD, Moving Averages).
    *   **Expected Output**: A technical analysis summary with key findings, annotated charts, and actionable insights on price trends and levels.

*   **Market News Analysis Task**
    *   **Description**: Gather and summarize the latest news, press releases, and brokerage reports, highlighting analyst ratings, target prices, and significant market developments.
    *   **Expected Output**: A news and sentiment summary, including key headlines, analyst opinions, and notable events affecting the stock, with possible visualizations.

*   **Portfolio Strategy Task**
    *   **Description**: Synthesize outputs from fundamental, technical, and news analysis to provide a clear Buy, Sell, or Hold recommendation with justification, suggesting entry/exit levels, target prices, and stop-losses.
    *   **Expected Output**: A holistic investment recommendation with rationale, actionable price levels, and risk considerations, potentially including summary tables or charts.

*   **Report Compilation Task**
    *   **Description**: Compile the outputs from all agents into a single, cohesive, and well-formatted markdown report, integrating all charts, data points, and recommendations.
    *   **Expected Output**: A comprehensive, easy-to-read report (in markdown) covering all aspects of the analysis, with integrated visuals, tables, and a clear final summary. The final report is saved as `final_report.md`.

## Tools

The crew utilizes custom tools to interact with financial data sources:

*   **YahooFinanceTechnicalTool**: Fetches and analyzes technical data (OHLCV, moving averages, RSI, MACD, Bollinger Bands) for Indian stocks using `yfinance`.
*   **YahooFinanceFundamentalTool**: Fetches and analyzes fundamental data (financial statements, key ratios) for Indian stocks using `yfinance`.
*   **MoneycontrolNewsTool**: Scrapes and summarizes the latest news, press releases, and analyst commentary for Indian stocks from Moneycontrol.

## Getting Started

### Prerequisites

*   Python 3.9+
*   `uv` (or `pip`) for dependency management

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/vishalpatel72/Stock_Market_Research_Analyst.git
    cd stock_market_research_analyst
    ```
2.  Install the dependencies:
    ```bash
    crewai install
    ```
3.  Create a `.env` file in the root directory and add any necessary environment variables (e.g., API keys for llm provider etc.).

### Running the Crew

To run the stock market research analysis for a specific stock (default is `RELIANCE.NS`):

```bash
crewai run
```

You can modify the `symbol` in `src/stock_market_research_analyst/main.py` to analyze a different stock.

## Configuration

Agent and task configurations are managed via YAML files:

*   `src/stock_market_research_analyst/config/agents.yaml`: Defines the roles, goals, and backstories for each agent.
*   `src/stock_market_research_analyst/config/tasks.yaml`: Defines the descriptions, expected outputs, and assigned agents for each task.

These files can be modified to fine-tune the behavior of the crew.
