import os
from datetime import datetime
from typing import List, Dict
from langchain.tools import tool
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from newsapi import NewsApiClient
from utils.config_loader import load_config

load_dotenv()

class NewsAggregator:
    """Main news aggregation class that handles multiple news sources"""
    
    def __init__(self):
        self.config = load_config()
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        self.newsapi_key = os.getenv('NEWS_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHAVANTAGE_API_KEY')
        
        # Initialize Tavily search (fallback only)
        if self.tavily_api_key:
            self.tavily_search = TavilySearch(
                api_key=self.tavily_api_key,
                topic="news",
                include_answer="advanced"
            )
        
        # Initialize NewsAPI client (primary source)
        self.newsapi_client = None
        if self.newsapi_key:
            self.newsapi_client = NewsApiClient(api_key=self.newsapi_key)
        
        # Load news sources from config
        self.news_sources = self.config.get('news_sources', {})
        self.api_limits = self.config.get('api_limits', {})
    
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
        """Search for news using NewsAPI (official Python client)."""
        try:
            if not self.newsapi_client:
                return []
            
            resp = self.newsapi_client.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                page_size=max_results,
            )
            return resp.get("articles", []) if isinstance(resp, dict) else []
        except Exception as e:
            print(f"Error in NewsAPI search: {e}")
            return []
    
    def search_tech_news(self, query: str) -> List[Dict]:
        """Search for technology news from specific domains using NewsAPI client."""
        tech_domains = self.news_sources.get('technology', [])
        # Convert source names to domains if needed
        domain_mapping = {
            "TechCrunch": "techcrunch.com",
            "Ars Technica": "arstechnica.com",
            "The Verge": "theverge.com",
            "Wired": "wired.com",
            "Engadget": "engadget.com",
            "VentureBeat": "venturebeat.com"
        }
        
        domains = [domain_mapping.get(source, source.lower().replace(" ", "") + ".com") for source in tech_domains]
        
        try:
            if not self.newsapi_client:
                return []
            
            max_results = self.api_limits.get('newsapi', {}).get('max_results', 10)
            
            resp = self.newsapi_client.get_everything(
                q=query,
                domains=",".join(domains),
                language='en',
                sort_by='publishedAt',
                page_size=max_results,
            )
            return resp.get("articles", []) if isinstance(resp, dict) else []
        except Exception as e:
            print(f"Error in tech news search: {e}")
            return []
    
    def search_business_news(self, query: str) -> List[Dict]:
        """Search for business news from financial domains using NewsAPI client."""
        business_domains = self.news_sources.get('business', [])
        # Convert source names to domains if needed
        domain_mapping = {
            "Bloomberg": "bloomberg.com",
            "Reuters Business": "reuters.com",
            "CNBC": "cnbc.com",
            "Wall Street Journal": "wsj.com",
            "Financial Times": "ft.com",
            "MarketWatch": "marketwatch.com"
        }
        
        domains = [domain_mapping.get(source, source.lower().replace(" ", "") + ".com") for source in business_domains]
        
        try:
            if not self.newsapi_client:
                return []
            
            max_results = self.api_limits.get('newsapi', {}).get('max_results', 10)
            
            resp = self.newsapi_client.get_everything(
                q=query,
                domains=",".join(domains),
                language='en',
                sort_by='publishedAt',
                page_size=max_results,
            )
            return resp.get("articles", []) if isinstance(resp, dict) else []
        except Exception as e:
            print(f"Error in business news search: {e}")
            return []
    
    def search_linkedin_news(self, query: str) -> List[Dict]:
        """Search for professional news and insights from LinkedIn using Tavily."""
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
        """Search for articles from Medium using Tavily."""
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
        
        # General news search - prioritize NewsAPI over Tavily
        if "general" in categories:
            newsapi_results = self.search_news_api(query, 10)
            # Only use Tavily as fallback if NewsAPI fails
            tavily_results = self.search_news_tavily(query, 5) if not newsapi_results else []
            aggregated_results["sources"]["general"] = {
                "newsapi": newsapi_results,
                "tavily": tavily_results
            }
            aggregated_results["total_articles"] += len(newsapi_results) + len(tavily_results)
        
        # Technology news - prioritize NewsAPI tech sources
        if "tech" in categories:
            tech_results = self.search_tech_news(query)
            # Only use Tavily for LinkedIn/Medium if NewsAPI tech results are insufficient
            linkedin_results = self.search_linkedin_news(query) if len(tech_results) < 5 else []
            medium_results = self.search_medium_articles(query) if len(tech_results) < 5 else []
            aggregated_results["sources"]["technology"] = {
                "tech_sources": tech_results,
                "linkedin": linkedin_results,
                "medium": medium_results
            }
            aggregated_results["total_articles"] += len(tech_results) + len(linkedin_results) + len(medium_results)
        
        # Business news - use NewsAPI only
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
        
        formatted_news = f"# 📰 General News about '{query}'\n\n"
        
        # Process Tavily results
        tavily_news = results["sources"]["general"].get("tavily", [])
        if tavily_news:
            formatted_news += "## 🔍 Web Search Results\n\n"
            for i, article in enumerate(tavily_news[:5], 1):
                title = article.get("title", "No title")
                content = article.get("content", "No content available")
                url = article.get("url", "")
                formatted_news += f"### {i}. {title}\n\n"
                formatted_news += f"{content[:200]}...\n\n"
                if url:
                    formatted_news += f"**Source:** [{url}]({url})\n\n"
                formatted_news += "---\n\n"
        
        # Process NewsAPI results
        newsapi_news = results["sources"]["general"].get("newsapi", [])
        if newsapi_news:
            formatted_news += "## 📰 News API Results\n\n"
            for i, article in enumerate(newsapi_news[:5], 1):
                title = article.get("title", "No title")
                description = article.get("description", "No description")
                url = article.get("url", "")
                source = article.get("source", {}).get("name", "Unknown")
                published = article.get("publishedAt", "")
                
                # Validate and clean URL
                if url and url.startswith('http'):
                    clean_url = url
                else:
                    clean_url = ""
                
                formatted_news += f"### {i}. {title}\n\n"
                formatted_news += f"{description}\n\n"
                formatted_news += f"**Source:** {source}\n"
                if published:
                    # Format published date
                    try:
                        pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                        formatted_date = pub_date.strftime('%B %d, %Y at %I:%M %p')
                        formatted_news += f"**Published:** {formatted_date}\n"
                    except:
                        formatted_news += f"**Published:** {published}\n"
                
                if clean_url:
                    formatted_news += f"**Link:** [{clean_url}]({clean_url})\n\n"
                formatted_news += "---\n\n"
        
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
        
        formatted_news = f"# 💻 Technology News about '{query}'\n\n"
        
        tech_sources = results["sources"]["technology"]
        
        # Tech sources (TechCrunch, Ars Technica, etc.)
        tech_articles = tech_sources.get("tech_sources", [])
        if tech_articles:
            formatted_news += "## 🔧 Tech Sources\n\n"
            for i, article in enumerate(tech_articles[:5], 1):
                title = article.get("title", "No title")
                description = article.get("description", "No description")
                url = article.get("url", "")
                source = article.get("source", {}).get("name", "Unknown")
                published = article.get("publishedAt", "")
                
                # Validate and clean URL
                if url and url.startswith('http'):
                    clean_url = url
                else:
                    clean_url = ""
                
                formatted_news += f"### {i}. {title}\n\n"
                formatted_news += f"{description}\n\n"
                formatted_news += f"**Source:** {source}\n"
                if published:
                    # Format published date
                    try:
                        pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                        formatted_date = pub_date.strftime('%B %d, %Y at %I:%M %p')
                        formatted_news += f"**Published:** {formatted_date}\n"
                    except:
                        formatted_news += f"**Published:** {published}\n"
                
                if clean_url:
                    formatted_news += f"**Link:** [{clean_url}]({clean_url})\n\n"
                formatted_news += "---\n\n"
        
        # LinkedIn insights
        linkedin_articles = tech_sources.get("linkedin", [])
        if linkedin_articles:
            formatted_news += "## 💼 LinkedIn Insights\n\n"
            for i, article in enumerate(linkedin_articles[:3], 1):
                title = article.get("title", "No title")
                content = article.get("content", "No content")
                url = article.get("url", "")
                formatted_news += f"### {i}. {title}\n\n"
                formatted_news += f"{content[:200]}...\n\n"
                if url:
                    formatted_news += f"**Link:** [{url}]({url})\n\n"
                formatted_news += "---\n\n"
        
        # Medium articles
        medium_articles = tech_sources.get("medium", [])
        if medium_articles:
            formatted_news += "## 📝 Medium Articles\n\n"
            for i, article in enumerate(medium_articles[:3], 1):
                title = article.get("title", "No title")
                content = article.get("content", "No content")
                url = article.get("url", "")
                formatted_news += f"### {i}. {title}\n\n"
                formatted_news += f"{content[:200]}...\n\n"
                if url:
                    formatted_news += f"**Link:** [{url}]({url})\n\n"
                formatted_news += "---\n\n"
        
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
        
        formatted_news = f"# 💼 Business News about '{query}'\n\n"
        
        business_sources = results["sources"]["business"]
        financial_articles = business_sources.get("financial_sources", [])
        
        if financial_articles:
            formatted_news += "## 📈 Financial Sources\n\n"
            for i, article in enumerate(financial_articles[:5], 1):
                title = article.get("title", "No title")
                description = article.get("description", "No description")
                url = article.get("url", "")
                source = article.get("source", {}).get("name", "Unknown")
                published = article.get("publishedAt", "")
                
                # Validate and clean URL
                if url and url.startswith('http'):
                    clean_url = url
                else:
                    clean_url = ""
                
                formatted_news += f"### {i}. {title}\n\n"
                formatted_news += f"{description}\n\n"
                formatted_news += f"**Source:** {source}\n"
                if published:
                    # Format published date
                    try:
                        pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                        formatted_date = pub_date.strftime('%B %d, %Y at %I:%M %p')
                        formatted_news += f"**Published:** {formatted_date}\n"
                    except:
                        formatted_news += f"**Published:** {published}\n"
                
                if clean_url:
                    formatted_news += f"**Link:** [{clean_url}]({clean_url})\n\n"
                formatted_news += "---\n\n"
        
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
        
        formatted_news = f"# 📰 Comprehensive News Coverage: '{query}'\n\n"
        formatted_news += f"**Total Articles Found:** {results['total_articles']}\n"
        formatted_news += f"**Search Time:** {results['timestamp']}\n\n"
        
        # General News
        if results["sources"].get("general"):
            formatted_news += "## 🌐 General News\n\n"
            
            tavily_news = results["sources"]["general"].get("tavily", [])
            if tavily_news:
                formatted_news += "### 🔍 Web Search Results\n\n"
                for i, article in enumerate(tavily_news[:3], 1):
                    title = article.get("title", "No title")
                    content = article.get("content", "No content")
                    formatted_news += f"**{i}. {title}**\n\n"
                    formatted_news += f"{content[:150]}...\n\n"
                    formatted_news += "---\n\n"
            
            newsapi_news = results["sources"]["general"].get("newsapi", [])
            if newsapi_news:
                formatted_news += "### 📰 News API Results\n\n"
                for i, article in enumerate(newsapi_news[:3], 1):
                    title = article.get("title", "No title")
                    description = article.get("description", "No description")
                    source = article.get("source", {}).get("name", "Unknown")
                    formatted_news += f"**{i}. {title}**\n\n"
                    formatted_news += f"{description}\n\n"
                    formatted_news += f"**Source:** {source}\n\n"
                    formatted_news += "---\n\n"
        
        # Technology News
        if results["sources"].get("technology"):
            formatted_news += "## 💻 Technology News\n\n"
            
            tech_sources = results["sources"]["technology"]
            tech_articles = tech_sources.get("tech_sources", [])
            if tech_articles:
                for i, article in enumerate(tech_articles[:3], 1):
                    title = article.get("title", "No title")
                    description = article.get("description", "No description")
                    source = article.get("source", {}).get("name", "Unknown")
                    formatted_news += f"**{i}. {title}**\n\n"
                    formatted_news += f"{description}\n\n"
                    formatted_news += f"**Source:** {source}\n\n"
                    formatted_news += "---\n\n"
        
        # Business News
        if results["sources"].get("business"):
            formatted_news += "## 💼 Business News\n\n"
            
            business_sources = results["sources"]["business"]
            financial_articles = business_sources.get("financial_sources", [])
            if financial_articles:
                for i, article in enumerate(financial_articles[:3], 1):
                    title = article.get("title", "No title")
                    description = article.get("description", "No description")
                    source = article.get("source", {}).get("name", "Unknown")
                    formatted_news += f"**{i}. {title}**\n\n"
                    formatted_news += f"{description}\n\n"
                    formatted_news += f"**Source:** {source}\n\n"
                    formatted_news += "---\n\n"
        
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
