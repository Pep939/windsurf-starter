# Crypto Trading Agency

A modular crypto trading agency built with Agency Swarm Framework that automates cryptocurrency trading, monitors wallet and token activity, and manages risks across multiple blockchains.

## Agents

### 1. Copy Trade Agent
- Monitors specific wallets for trading activity
- Replicates trades on Solana with optional multi-chain support
- Executes trades based on predefined criteria

### 2. Market Sentinel Agent
- Monitors token activity across blockchains
- Identifies trends and trading opportunities
- Performs sentiment analysis on social media and news

### 3. Risk Management Agent
- Enforces risk management rules
- Calculates position sizes and exposure limits
- Manages stop-loss and take-profit parameters

### 4. Blockchain Monitor Agent
- Tracks transaction data from multiple blockchains
- Provides real-time updates to other agents
- Supports Solana, Ethereum, BSC, and Polygon

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Copy `.env.sample` to `.env` and fill in your API keys
4. Run the agency:
```bash
python main.py
```

## Project Structure
```
├── tools/
│   ├── copy_trade_agent/
│   ├── market_sentinel_agent/
│   ├── risk_management_agent/
│   └── blockchain_monitor_agent/
├── requirements.txt
├── main.py
└── agency.py
```

## Deployment
The project is configured for deployment on Railway. Each agent can be deployed independently.

## Environment Variables
Required environment variables:
- `SOLANA_RPC_URL`: Your Solana RPC endpoint
- `ETHEREUM_RPC_URL`: Your Ethereum RPC endpoint
- `TELEGRAM_BOT_TOKEN`: For notifications
- `API_KEYS`: Various API keys for data providers

## License
MIT License
