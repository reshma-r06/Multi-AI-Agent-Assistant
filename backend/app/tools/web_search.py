from langchain.tools import Tool
from duckduckgo_search import DDGS
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class WebSearchTool:
    """Tool for performing web searches"""
    
    def __init__(self, max_results: int = 5):
        self.max_results = max_results
        self.ddgs = DDGS()
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Perform a web search and return results"""
        try:
            results = []
            search_results = self.ddgs.text(
                query, 
                max_results=self.max_results
            )
            
            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return []
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results as a string"""
        if not results:
            return "No results found."
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"{i}. {result['title']}\n"
                f"   URL: {result['url']}\n"
                f"   {result['snippet']}\n"
            )
        
        return "\n".join(formatted)
    
    def as_langchain_tool(self) -> Tool:
        """Convert to LangChain Tool"""
        def search_wrapper(query: str) -> str:
            results = self.search(query)
            return self.format_results(results)
        
        return Tool(
            name="web_search",
            func=search_wrapper,
            description=(
                "Useful for searching the web for current information, "
                "market data, competitor analysis, or any real-time information. "
                "Input should be a search query string."
            )
        )


class CalculatorTool:
    """Simple calculator tool for agents"""
    
    @staticmethod
    def calculate(expression: str) -> str:
        """Safely evaluate mathematical expressions"""
        try:
            # Remove any dangerous characters
            safe_expr = ''.join(
                c for c in expression 
                if c in '0123456789+-*/(). '
            )
            result = eval(safe_expr)
            return f"Result: {result}"
        except Exception as e:
            return f"Error calculating: {str(e)}"
    
    @staticmethod
    def as_langchain_tool() -> Tool:
        """Convert to LangChain Tool"""
        return Tool(
            name="calculator",
            func=CalculatorTool.calculate,
            description=(
                "Useful for performing mathematical calculations. "
                "Input should be a mathematical expression like '2+2' or '10*5'."
            )
        )