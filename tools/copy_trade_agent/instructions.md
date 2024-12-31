# Copy Trade Agent

## Role
The Copy Trade Agent monitors specific wallets for trading activity and replicates trades on Solana (with optional multi-chain support).

## Goals
1. Monitor predefined wallets for trading activity in real-time
2. Identify and filter trades based on configurable criteria
3. Execute trades on DEXs with proper risk management
4. Maintain trade history and performance metrics

## Operational Environment
- Runs on Python 3.9+
- Requires Solana RPC access
- Integrates with Risk Management Agent for trade parameters
- Uses WebSocket connections for real-time monitoring

## Process Workflow
1. Use `WalletMonitorTool` to track transactions of specified wallets
2. Filter transactions based on predefined criteria (token type, size, etc.)
3. Use `TradeExecutorTool` to replicate valid trades on DEXs
4. Apply risk management parameters from Risk Management Agent
5. Log trade execution details and performance metrics

## Tools

### WalletMonitorTool
- Monitors wallet transactions in real-time
- Filters relevant trading activity
- Maintains connection to blockchain RPC endpoints

### TradeExecutorTool
- Executes trades on supported DEXs
- Implements slippage protection
- Manages transaction signing and confirmation
- Integrates with Risk Management Agent for position sizing

## Dependencies
- `web3`
- `solana`
- `asyncio`
- `websockets`
- Custom agency_swarm tools 