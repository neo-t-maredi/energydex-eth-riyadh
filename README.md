# EnergyDEX - Industrial-Grade DeFi Monitoring

**Built for ETH Riyadh 2026 by Neo Maredi**

Real-time DEX arbitrage detection and trading analytics platform. Bridging 15 years of industrial automation expertise with DeFi protocols.

## Features

### Core Functionality (Implemented)
- **Live Price Monitoring** - Real-time ETH/USDC prices from Uniswap V2 & SushiSwap
- **Multi-DEX Comparison** - Instant spread analysis across DEXs
- **Arbitrage Detection** - Automated opportunity identification with profit calculations
- **Historical Data** - SQLite-based price history and analytics
- **Trade Simulation** - Risk-free strategy testing with detailed breakdowns
- **Profit Calculator** - Gas fees, slippage, and DEX fee modeling

### Coming Soon (Feb 1-2)
- **Web3 Wallet Integration** - MetaMask connect
- **On-Chain Execution** - Live testnet trading
- **Transaction History** - On-chain activity tracking
- **Portfolio Dashboard** - Real-time token balances

## Architecture
```
EnergyDEX/
├── backend/          # Python + Flask + WebSocket
│   └── src/
│       ├── price_monitor.py       # Live Uniswap/Sushi feeds
│       ├── dex_handler.py         # Multi-DEX aggregation
│       ├── arbitrage_detector.py  # Opportunity engine
│       ├── historical_data.py     # SQLite storage
│       ├── trade_simulator.py     # Execution simulation
│       ├── profit_calculator.py   # Financial modeling
│       └── api_server.py          # REST + WebSocket API
│
└── frontend/         # Next.js 15 + TypeScript
    └── src/
        ├── app/                   # Pages & layouts
        ├── hooks/                 # WebSocket & custom hooks
        └── utils/                 # API client
```

## Quick Start

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add your Alchemy API key to .env
echo "ALCHEMY_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY" > .env

# Start the API server
python3 src/api_server.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

## Tech Stack

**Backend:**
- Python 3.12
- Flask + Flask-SocketIO (WebSocket)
- Web3.py (Ethereum interaction)
- SQLite (data persistence)
- Pandas (analytics)

**Frontend:**
- Next.js 15 (React 19)
- TypeScript
- Tailwind CSS v4
- Three.js + React Three Fiber (3D)
- Framer Motion (animations)
- Socket.io-client (real-time updates)

**Blockchain:**
- Ethereum Mainnet (live prices)
- Alchemy RPC (node provider)
- Uniswap V2 Protocol
- SushiSwap Protocol

## API Endpoints
```
GET  /api/health                    # Health check
GET  /api/prices/current            # Current prices from all DEXs
GET  /api/prices/comparison         # Price spread analysis
POST /api/arbitrage/detect          # Find arbitrage opportunities
GET  /api/historical/prices         # Historical price data
GET  /api/historical/stats          # Price statistics
POST /api/trade/simulate            # Simulate trade execution
GET  /api/trade/statistics          # Trading performance stats
POST /api/profit/calculate          # Calculate profit breakdown
```

**WebSocket Events:**
- `price_update` - Real-time price feeds (5s interval)
- `arbitrage_alert` - Profitable opportunity notifications

## Why EnergyDEX?

**The Angle:** Industrial automation engineer bringing SCADA control room precision to DeFi.

I've spent 15 years monitoring billion-dollar oil & gas infrastructure at Uthmaniyah Gas Processing Plant. The same systematic monitoring, alert systems, and data analysis that keeps a $794M facility running? That's what I'm bringing to DeFi trading.

**The Vision:** 
- Control room aesthetic (not another generic DEX interface)
- Industrial-grade reliability
- Real-world asset expertise (UGPT Protocol, Stratum Protocol)
- Energy sector meets blockchain

## Roadmap

**Phase 1: Foundation** (Completed Jan 31)
- Live price monitoring
- Arbitrage detection
- Dashboard UI

**Phase 2: Web3 Integration** (Feb 1-2)
- Wallet connection
- On-chain trading
- Transaction history

**Phase 3: ETH Riyadh Demo** (Feb 3-4)
- Live showcase
- Testnet deployment
- Networking

**Phase 4: Production** (Post-conference)
- Mainnet deployment
- Additional DEX support
- Advanced strategies

## About the Builder

**Neo Maredi**
- Industrial Automation Engineer @ Uthmaniyah Gas Processing (Saudi Aramco)
- 15 years in oil & gas automation (PLCs, SCADA, control systems)
- Blockchain Developer (Solidity, Foundry, Web3)
- Based in Dammam, Saudi Arabia

**Other Projects:**
- UGPT Protocol (Gas facility tokenization)
- Stratum Protocol (Oil-backed stablecoin)

## License

MIT License - Built in 72 hours for ETH Riyadh 2026

---

**"From Control Rooms to Smart Contracts"**
