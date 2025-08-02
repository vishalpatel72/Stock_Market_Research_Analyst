from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from src.stock_market_research_analyst.tools.custom_tool import (
    YahooFinanceFundamentalTool,
    YahooFinanceTechnicalTool,
    MoneycontrolNewsTool
)
from crewai_tools import WebsiteSearchTool, ScrapeWebsiteTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class StockMarketResearchAnalyst():
    """StockMarketResearchAnalyst crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Instantiate tools
    fundamental_tool = YahooFinanceFundamentalTool()
    technical_tool = YahooFinanceTechnicalTool()
    news_tool = MoneycontrolNewsTool()
    # web_search_tool = WebsiteSearchTool()  # Temporarily disabled
    scrape_website_tool = ScrapeWebsiteTool()

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def fundamental_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['fundamental_analyst'],
            tools=[self.fundamental_tool],  # Only custom tool
            verbose=True
        )

    @agent
    def technical_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['technical_analyst'],
            tools=[self.technical_tool],  # Only custom tool
            verbose=True
        )

    @agent
    def market_news_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['market_news_analyst'],
            tools=[self.news_tool, self.scrape_website_tool],  # Only custom and scrape tool
            verbose=True
        )

    @agent
    def portfolio_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['portfolio_strategist'],
            tools=[],  # No direct tools, synthesizes outputs from other agents
            verbose=True
        )

    @agent
    def report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['report_writer'],
            tools=[],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def fundamental_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['fundamental_analysis_task'],
        )

    @task
    def technical_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['technical_analysis_task'],
        )

    @task
    def market_news_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['market_news_analysis_task'],
        )

    @task
    def portfolio_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config['portfolio_strategy_task'],
        )

    @task
    def report_compilation_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_compilation_task'],
            output_file='final_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockMarketResearchAnalyst crew with optimized dependencies"""
        # Define tasks with context dependencies
        fundamental_task = self.fundamental_analysis_task()
        technical_task = self.technical_analysis_task()
        news_task = self.market_news_analysis_task()

        portfolio_strategy_task = Task(
            config=self.tasks_config['portfolio_strategy_task'],
            agent=self.portfolio_strategist(),
            context=[fundamental_task, technical_task, news_task]
        )

        report_task = Task(
            config=self.tasks_config['report_compilation_task'],
            agent=self.report_writer(),
            output_file='final_report.md',
            context=[portfolio_strategy_task, fundamental_task, technical_task, news_task]
        )

        return Crew(
            agents=[
                self.fundamental_analyst(),
                self.technical_analyst(),
                self.market_news_analyst(),
                self.portfolio_strategist(),
                self.report_writer()
            ],
            tasks=[
                fundamental_task,
                technical_task,
                news_task,
                portfolio_strategy_task,
                report_task
            ],
            process=Process.sequential,  # Sequential, but with explicit context/dependencies
            verbose=True,
        )
