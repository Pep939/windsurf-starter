from agency_swarm.tools import BaseTool
from pydantic import Field, ConfigDict
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional, Callable
import asyncio
import json

load_dotenv()

class SentimentAnalyzerTool(BaseTool):
    """
    Tool for analyzing market sentiment from social media and news sources.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    target_tokens: List[str] = Field(
        ...,
        description="List of tokens to monitor sentiment for"
    )
    
    sentiment_threshold: float = Field(
        default=0.2,
        description="Minimum sentiment score to trigger alert"
    )
    
    min_mentions: int = Field(
        default=10,
        description="Minimum number of mentions required"
    )
    
    transaction_handlers: List[Callable[[Dict], None]] = Field(
        default_factory=list,
        description="List of callback functions to handle sentiment alerts"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        self.transaction_handlers = []
        
    def add_transaction_handler(self, handler: Callable[[Dict], None]):
        """Add a callback function to handle sentiment alerts."""
        self.transaction_handlers.append(handler)
    
    async def start_analysis(self):
        """Start sentiment analysis."""
        try:
            print("Sentiment analyzer started...")
            while True:
                # Placeholder for actual sentiment analysis logic
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
        except Exception as e:
            print(f"Error in sentiment analyzer: {e}")
            return False
        
        return True
    
    def run(self):
        """
        Main execution method for the tool.
        This tool is primarily used through its start_analysis method.
        """
        return "Sentiment analyzer initialized successfully"

if __name__ == "__main__":
    # Test the tool
    tool = SentimentAnalyzerTool(
        target_tokens=["SOL", "BTC", "ETH"],
        sentiment_threshold=0.2,
        min_mentions=10
    )
    
    def print_sentiment(sentiment):
        print(json.dumps(sentiment, indent=2))
    
    tool.add_transaction_handler(print_sentiment)
    
    # Run the analyzer
    asyncio.run(tool.start_analysis()) 