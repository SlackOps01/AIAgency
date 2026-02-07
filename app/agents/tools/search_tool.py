from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai import RunContext, Tool
import asyncio
import random


async def search_with_retry(
    query: str,
    max_results: int = 5,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> str:
    """Search DuckDuckGo with exponential backoff retry logic."""
    
    # Get the original tool function
    original_tool = duckduckgo_search_tool(max_results=max_results)
    
    last_error = None
    for attempt in range(max_retries):
        try:
            # Call the underlying search
            result = await original_tool.function(query)
            return result
            
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Search failed (attempt {attempt + 1}), retrying in {delay:.2f}s...")
                await asyncio.sleep(delay)
            else:
                print(f"Search failed after {max_retries} attempts")
    
    return f"Search failed: {str(last_error)}"


# Create a custom tool wrapper
def robust_search_tool(max_results: int = 5, max_retries: int = 3) -> Tool:
    """Returns a DuckDuckGo search tool with retry logic."""
    
    async def search(ctx: RunContext, query: str) -> str:
        """Search DuckDuckGo for information."""
        return await search_with_retry(query, max_results, max_retries)
    
    return Tool(search, name="web_search")