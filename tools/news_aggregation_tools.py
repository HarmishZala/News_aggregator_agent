import os
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from langchain.tools import tool
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

class NewsAggregator:
    """Main news aggregation class that handles multiple news sources"""
    
    def __init__(self):
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        self.newsapi_key = os.getenv('NEWS_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHAVANTAGE_API_KEY')
        
        # Initialize Tavily search
        if self.tavily_api_key:
            self.tavily_search = TavilySearch(
                api_key=self.tavily_api_key,
                topic="news",
                include_answer="advanced"
            )
    
    def search_news_tavily(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for news using Tavily API"""
        try:
            if not self.tavily_api_key:
                return []
            
            result = self.tavily_search.invoke({
                "query": f"latest news about {query}",
                "max_results": max_results
            })
            
            if isinstance(result, dict) and "results" in result:
                return result["results"]
            return []
        except Exception as e:
            print(f"Error in Tavily search: {e}")
            return []
    
    def search_news_api(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for news using NewsAPI"""
        try:
            if not self.newsapi_key:
                return []
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": self.newsapi_key,
                "pageSize": max_results,
                "sortBy": "publishedAt",
                "language": "en"
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("articles", [])
            return []
        except Exception as e:
            print(f"Error in NewsAPI search: {e}")
            return []
    
    def search_tech_news(self, query: str) -> List[Dict]:
        """Search for technology news from specific sources"""
        tech_sources = [
            "techcrunch.com",
            "arstechnica.com", 
            "theverge.com",
            "wired.com",
            "engadget.com",
            "venturebeat.com"
        ]
        
        try:
            if not self.newsapi_key:
                return []
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": self.newsapi_key,
                "sources": ",".join(tech_sources),
                "pageSize": 10,
                "sortBy": "publishedAt"
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("articles", [])
            return []
        except Exception as e:
            print(f"Error in tech news search: {e}")
            return []
    
    def search_business_news(self, query: str) -> List[Dict]:
        """Search for business news from financial sources"""
        business_sources = [
            "bloomberg.com",
            "reuters.com",
            "cnbc.com",
            "wsj.com",
            "ft.com",
            "marketwatch.com"
        ]
        
        try:
            if not self.newsapi_key:
                return []
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": self.newsapi_key,
                "sources": ",".join(business_sources),
                "pageSize": 10,
                "sortBy": "publishedAt"
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("articles", [])
            return []
        except Exception as e:
            print(f"Error in business news search: {e}")
            return []
    
    def search_linkedin_news(self, query: str) -> List[Dict]:
        """Search for professional news and insights from LinkedIn"""
        try:
            if not self.tavily_api_key:
                return []
            
            result = self.tavily_search.invoke({
                "query": f"site:linkedin.com {query} news insights",
                "max_results": 5
            })
            
            if isinstance(result, dict) and "results" in result:
                return result["results"]
            return []
        except Exception as e:
            print(f"Error in LinkedIn search: {e}")
            return []
    
    def search_medium_articles(self, query: str) -> List[Dict]:
        """Search for articles from Medium"""
        try:
            if not self.tavily_api_key:
                return []
            
            result = self.tavily_search.invoke({
                "query": f"site:medium.com {query}",
                "max_results": 5
            })
            
            if isinstance(result, dict) and "results" in result:
                return result["results"]
            return []
        except Exception as e:
            print(f"Error in Medium search: {e}")
            return []
    
    def aggregate_news(self, query: str, categories: List[str] = None) -> Dict:
        """Aggregate news from multiple sources based on query and categories"""
        if categories is None:
            categories = ["general", "tech", "business"]
        
        aggregated_results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "sources": {},
            "total_articles": 0
        }
        
        # General news search
        if "general" in categories:
            tavily_results = self.search_news_tavily(query, 10)
            newsapi_results = self.search_news_api(query, 10)
            aggregated_results["sources"]["general"] = {
                "tavily": tavily_results,
                "newsapi": newsapi_results
            }
            aggregated_results["total_articles"] += len(tavily_results) + len(newsapi_results)
        
        # Technology news
        if "tech" in categories:
            tech_results = self.search_tech_news(query)
            linkedin_results = self.search_linkedin_news(query)
            medium_results = self.search_medium_articles(query)
            aggregated_results["sources"]["technology"] = {
                "tech_sources": tech_results,
                "linkedin": linkedin_results,
                "medium": medium_results
            }
            aggregated_results["total_articles"] += len(tech_results) + len(linkedin_results) + len(medium_results)
        
        # Business news
        if "business" in categories:
            business_results = self.search_business_news(query)
            aggregated_results["sources"]["business"] = {
                "financial_sources": business_results
            }
            aggregated_results["total_articles"] += len(business_results)
        
        return aggregated_results

# Initialize the news aggregator
news_aggregator = NewsAggregator()

# LangChain tools for the agent
@tool
def search_general_news(query: str) -> str:
    """
    Search for general news articles about a specific topic.
    
    Args:
        query (str): The topic or keywords to search for in news
        
    Returns:
        str: Formatted news articles with titles, descriptions, and sources
    """
    try:
        results = news_aggregator.aggregate_news(query, ["general"])
        
        if not results["sources"].get("general"):
            return f"No general news found for '{query}'"
        
        formatted_news = f"📰 General News about '{query}':\n\n"
        
        # Process Tavily results
        tavily_news = results["sources"]["general"].get("tavily", [])
        if tavily_news:
            formatted_news += "🔍 Web Search Results:\n"
            for i, article in enumerate(tavily_news[:5], 1):
                title = article.get("title", "No title")
                content = article.get("content", "No content available")
                url = article.get("url", "")
                formatted_news += f"{i}. **{title}**\n"
                formatted_news += f"   {content[:200]}...\n"
                if url:
                    formatted_news += f"   Source: {url}\n\n"
        
        # Process NewsAPI results
        newsapi_news = results["sources"]["general"].get("newsapi", [])
        if newsapi_news:
            formatted_news += "📰 News API Results:\n"
            for i, article in enumerate(newsapi_news[:5], 1):
                title = article.get("title", "No title")
                description = article.get("description", "No description")
                url = article.get("url", "")
                source = article.get("source", {}).get("name", "Unknown")
                published = article.get("publishedAt", "")
                formatted_news += f"{i}. **{title}**\n"
                formatted_news += f"   {description}\n"
                formatted_news += f"   Source: {source}\n"
                if published:
                    formatted_news += f"   Published: {published}\n"
                if url:
                    formatted_news += f"   Link: {url}\n\n"
        
        return formatted_news
        
    except Exception as e:
        return f"Error searching for general news: {str(e)}"

@tool
def search_technology_news(query: str) -> str:
    """
    Search for technology news and articles from tech sources, LinkedIn, and Medium.
    
    Args:
        query (str): The technology topic to search for
        
    Returns:
        str: Formatted technology news and articles
    """
    try:
        results = news_aggregator.aggregate_news(query, ["tech"])
        
        if not results["sources"].get("technology"):
            return f"No technology news found for '{query}'"
        
        formatted_news = f"💻 Technology News about '{query}':\n\n"
        
        tech_sources = results["sources"]["technology"]
        
        # Tech sources (TechCrunch, Ars Technica, etc.)
        tech_articles = tech_sources.get("tech_sources", [])
        if tech_articles:
            formatted_news += "🔧 Tech Sources:\n"
            for i, article in enumerate(tech_articles[:5], 1):
                title = article.get("title", "No title")
                description = article.get("description", "No description")
                url = article.get("url", "")
                source = article.get("source", {}).get("name", "Unknown")
                published = article.get("publishedAt", "")
                formatted_news += f"{i}. **{title}**\n"
                formatted_news += f"   {description}\n"
                formatted_news += f"   Source: {source}\n"
                if published:
                    formatted_news += f"   Published: {published}\n"
                if url:
                    formatted_news += f"   Link: {url}\n\n"
        
        # LinkedIn insights
        linkedin_articles = tech_sources.get("linkedin", [])
        if linkedin_articles:
            formatted_news += "💼 LinkedIn Insights:\n"
            for i, article in enumerate(linkedin_articles[:3], 1):
                title = article.get("title", "No title")
                content = article.get("content", "No content")
                url = article.get("url", "")
                formatted_news += f"{i}. **{title}**\n"
                formatted_news += f"   {content[:200]}...\n"
                if url:
                    formatted_news += f"   Link: {url}\n\n"
        
        # Medium articles
        medium_articles = tech_sources.get("medium", [])
        if medium_articles:
            formatted_news += "📝 Medium Articles:\n"
            for i, article in enumerate(medium_articles[:3], 1):
                title = article.get("title", "No title")
                content = article.get("content", "No content")
                url = article.get("url", "")
                formatted_news += f"{i}. **{title}**\n"
                formatted_news += f"   {content[:200]}...\n"
                if url:
                    formatted_news += f"   Link: {url}\n\n"
        
        return formatted_news
        
    except Exception as e:
        return f"Error searching for technology news: {str(e)}"

@tool
def search_business_news(query: str) -> str:
    """
    Search for business and financial news from reputable financial sources.
    
    Args:
        query (str): The business topic to search for
        
    Returns:
        str: Formatted business news articles
    """
    try:
        results = news_aggregator.aggregate_news(query, ["business"])
        
        if not results["sources"].get("business"):
            return f"No business news found for '{query}'"
        
        formatted_news = f"💼 Business News about '{query}':\n\n"
        
        business_sources = results["sources"]["business"]
        financial_articles = business_sources.get("financial_sources", [])
        
        if financial_articles:
            formatted_news += "📈 Financial Sources:\n"
            for i, article in enumerate(financial_articles[:5], 1):
                title = article.get("title", "No title")
                description = article.get("description", "No description")
                url = article.get("url", "")
                source = article.get("source", {}).get("name", "Unknown")
                published = article.get("publishedAt", "")
                formatted_news += f"{i}. **{title}**\n"
                formatted_news += f"   {description}\n"
                formatted_news += f"   Source: {source}\n"
                if published:
                    formatted_news += f"   Published: {published}\n"
                if url:
                    formatted_news += f"   Link: {url}\n\n"
        
        return formatted_news
        
    except Exception as e:
        return f"Error searching for business news: {str(e)}"

@tool
def search_comprehensive_news(query: str) -> str:
    """
    Search for comprehensive news coverage across all categories (general, tech, business).
    
    Args:
        query (str): The topic to search for across all news categories
        
    Returns:
        str: Comprehensive formatted news coverage from all sources
    """
    try:
        results = news_aggregator.aggregate_news(query, ["general", "tech", "business"])
        
        formatted_news = f"📰 Comprehensive News Coverage: '{query}'\n"
        formatted_news += f"Total Articles Found: {results['total_articles']}\n"
        formatted_news += f"Search Time: {results['timestamp']}\n\n"
        
        # General News
        if results["sources"].get("general"):
            formatted_news += "🌐 GENERAL NEWS\n"
            formatted_news += "=" * 50 + "\n"
            
            tavily_news = results["sources"]["general"].get("tavily", [])
            if tavily_news:
                formatted_news += "🔍 Web Search Results:\n"
                for i, article in enumerate(tavily_news[:3], 1):
                    title = article.get("title", "No title")
                    content = article.get("content", "No content")
                    formatted_news += f"{i}. **{title}**\n"
                    formatted_news += f"   {content[:150]}...\n\n"
            
            newsapi_news = results["sources"]["general"].get("newsapi", [])
            if newsapi_news:
                formatted_news += "📰 News API Results:\n"
                for i, article in enumerate(newsapi_news[:3], 1):
                    title = article.get("title", "No title")
                    description = article.get("description", "No description")
                    source = article.get("source", {}).get("name", "Unknown")
                    formatted_news += f"{i}. **{title}**\n"
                    formatted_news += f"   {description}\n"
                    formatted_news += f"   Source: {source}\n\n"
        
        # Technology News
        if results["sources"].get("technology"):
            formatted_news += "\n💻 TECHNOLOGY NEWS\n"
            formatted_news += "=" * 50 + "\n"
            
            tech_sources = results["sources"]["technology"]
            tech_articles = tech_sources.get("tech_sources", [])
            if tech_articles:
                for i, article in enumerate(tech_articles[:3], 1):
                    title = article.get("title", "No title")
                    description = article.get("description", "No description")
                    source = article.get("source", {}).get("name", "Unknown")
                    formatted_news += f"{i}. **{title}**\n"
                    formatted_news += f"   {description}\n"
                    formatted_news += f"   Source: {source}\n\n"
        
        # Business News
        if results["sources"].get("business"):
            formatted_news += "\n💼 BUSINESS NEWS\n"
            formatted_news += "=" * 50 + "\n"
            
            business_sources = results["sources"]["business"]
            financial_articles = business_sources.get("financial_sources", [])
            if financial_articles:
                for i, article in enumerate(financial_articles[:3], 1):
                    title = article.get("title", "No title")
                    description = article.get("description", "No description")
                    source = article.get("source", {}).get("name", "Unknown")
                    formatted_news += f"{i}. **{title}**\n"
                    formatted_news += f"   {description}\n"
                    formatted_news += f"   Source: {source}\n\n"
        
        return formatted_news
        
    except Exception as e:
        return f"Error in comprehensive news search: {str(e)}"

# Tool list for the agent
news_tool_list = [
    search_general_news,
    search_technology_news,
    search_business_news,
    search_comprehensive_news
]
