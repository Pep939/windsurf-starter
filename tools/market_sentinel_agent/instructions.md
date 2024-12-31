# Market Sentinel Agent

## Role
The Market Sentinel Agent monitors token activity across blockchains to identify trends, token launches, and trading opportunities. It analyzes market sentiment and provides trading signals to other agents.

## Goals
1. Monitor token price and volume movements across DEXs
2. Analyze social media sentiment for emerging trends
3. Identify potential trading opportunities
4. Generate and distribute trading signals
5. Track market metrics and maintain historical data

## Operational Environment
- Runs on Python 3.9+
- Requires access to DEX APIs and blockchain RPCs
- Integrates with social media APIs for sentiment analysis
- Uses WebSocket connections for real-time price data
- Maintains connection to database for historical data

## Process Workflow
1. Use `TokenScannerTool` to monitor DEX activity
2. Use `SentimentAnalyzerTool` to process social media data
3. Combine on-chain and sentiment data to generate signals
4. Distribute signals to Copy Trade Agent
5. Log market data and performance metrics

## Tools

### TokenScannerTool
- Monitors token price and volume across DEXs
- Tracks liquidity changes and market depth
- Identifies unusual trading activity
- Maintains historical price and volume data

### SentimentAnalyzerTool
- Processes social media data from Twitter, Discord, etc.
- Analyzes news and announcements
- Calculates sentiment scores
- Identifies trending topics and tokens

## Dependencies
- `requests`
- `websockets`
- `pandas`
- `numpy`
- `textblob` (for sentiment analysis)
- `tweepy` (for Twitter API)
- Custom agency_swarm tools 