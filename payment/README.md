# 🪙 IOIO Payment System - Solana Integration

Complete payment system for IOIO Game using Solana blockchain (Devnet/Testnet).

## 📁 Folder Structure

```
payment/
├── smart_contract/          # Solana smart contract (Rust/Anchor)
│   ├── programs/
│   │   └── ioio-game/
│   │       ├── src/
│   │       │   └── lib.rs   # Main smart contract code
│   │       └── Cargo.toml
│   └── Anchor.toml
├── templates/
│   └── test_payment.html    # Test web interface
├── solana_adapter.py        # Python Solana integration
├── test_payment.py          # Standalone test server
├── requirements.txt         # Python dependencies
├── config.example.py        # Configuration template
└── README.md               # This file
```

## 🎯 What This Does

1. **Smart Contract**: Manages game sessions, payments, and leaderboard on Solana blockchain
2. **Payment System**: Generates QR codes for Solana Pay
3. **Test Interface**: Web page to test payment flow before integration
4. **Python Adapter**: Bridge between your Python app and Solana blockchain

## 🚀 Quick Start Guide

### Step 1: Install Dependencies

```bash
cd payment
pip install -r requirements.txt
```

### Step 2: Deploy Smart Contract (Solana Playground)

#### 2.1 Open Solana Playground
Go to: **https://beta.solpg.io/**

#### 2.2 Create New Project
1. Click "Create a new project"
2. Select "Anchor" framework
3. Name it: `ioio-game`

#### 2.3 Copy Smart Contract Code
1. Open `payment/smart_contract/programs/ioio-game/src/lib.rs`
2. **COPY ALL THE CODE** from that file
3. In Solana Playground, **PASTE** into `lib.rs` (replace everything)

#### 2.4 Update Cargo.toml
1. Open `payment/smart_contract/programs/ioio-game/Cargo.toml`
2. **COPY ALL THE CODE**
3. In Solana Playground, open `Cargo.toml`
4. **PASTE** (replace everything)

#### 2.5 Build & Deploy
1. Click **"Build"** button (wait ~30 seconds)
2. If build succeeds, click **"Deploy"**
3. **IMPORTANT**: Copy the **Program ID** that appears
   - Example: `7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU`
   - **Save this!** You'll need it later

#### 2.6 Get Your Wallet Address
1. In Solana Playground, look at bottom-left
2. You'll see your wallet address (starts with a number/letter)
3. **Copy this address**
4. **Save it!** This is your GAME_WALLET

### Step 3: Create IOIO Token

#### Option A: Using Token Creator (Easiest)

1. Go to: **https://www.solaneyes.com/token-creator/**
2. Connect your Phantom wallet
3. Switch wallet to **Devnet** mode:
   - Open Phantom
   - Settings → Developer Settings → Testnet Mode → ON
   - Select "Devnet" network
4. Fill in token details:
   - **Name**: IOIO
   - **Symbol**: IOIO
   - **Decimals**: 2
   - **Supply**: 1000000 (1 million)
5. Click "Create Token"
6. **Copy the Token Mint Address** that appears
7. **Save it!** This is your IOIO_TOKEN_MINT

#### Option B: Using Solana Playground

1. In Solana Playground terminal, run:
```bash
spl-token create-token --decimals 2
```
2. **Copy the token address** that appears
3. Create token account:
```bash
spl-token create-account <YOUR_TOKEN_ADDRESS>
```
4. Mint tokens:
```bash
spl-token mint <YOUR_TOKEN_ADDRESS> 1000000
```

### Step 4: Configure Test System

1. Open `payment/config.example.py`
2. Copy the 3 values you saved:
   ```python
   PROGRAM_ID = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"  # From Step 2.5
   IOIO_TOKEN_MINT = "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU"  # From Step 3
   GAME_WALLET = "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9"  # From Step 2.6
   ```
3. Save as `config.py` (remove `.example`)

### Step 5: Run Test Server

```bash
python test_payment.py
```

Open browser to: **http://127.0.0.1:5001**

### Step 6: Test Payment Flow

1. **Configure**: Enter your 3 values in the web interface
2. **Generate QR**: Click "Generate QR Code"
3. **Pay**: Scan QR with Phantom wallet (Devnet mode)
4. **Wait**: System monitors payment automatically
5. **Confirm**: When paid, "Start Game" button enables
6. **Play**: Click button to simulate game start
7. **Score**: Submit a test score

## 📋 What You Need to Copy

### From Solana Playground → Your Config

| What | Where to Find | Where to Paste |
|------|---------------|----------------|
| **Program ID** | After clicking "Deploy" | `config.py` → `PROGRAM_ID` |
| **Wallet Address** | Bottom-left of Playground | `config.py` → `GAME_WALLET` |

### From Token Creator → Your Config

| What | Where to Find | Where to Paste |
|------|---------------|----------------|
| **Token Mint** | After creating token | `config.py` → `IOIO_TOKEN_MINT` |

## 🔧 Detailed Instructions

### A. Solana Playground Steps (with Screenshots)

#### 1. Open Solana Playground
```
URL: https://beta.solpg.io/
```

#### 2. Create Project
- Click "+ Create a new project"
- Select "Anchor (Rust)"
- Name: `ioio-game`

#### 3. Replace Code
**File: `lib.rs`**
- Location: `programs/ioio-game/src/lib.rs`
- Action: Select all (Ctrl+A) → Delete → Paste new code
- Source: `payment/smart_contract/programs/ioio-game/src/lib.rs`

**File: `Cargo.toml`**
- Location: `programs/ioio-game/Cargo.toml`
- Action: Select all (Ctrl+A) → Delete → Paste new code
- Source: `payment/smart_contract/programs/ioio-game/Cargo.toml`

#### 4. Build
- Click "🔨 Build" button (top toolbar)
- Wait for "Build successful ✅"
- If errors, check code was copied correctly

#### 5. Deploy
- Click "🚀 Deploy" button
- Wait for deployment
- **COPY THIS**: Program ID appears in console
  ```
  Program Id: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU
  ```

#### 6. Get Wallet
- Look at bottom-left corner
- See: `👛 5tzFk...uAi9`
- Click to copy full address
- **SAVE THIS**: This is your GAME_WALLET

### B. Token Creation Steps

#### Using Solaneyes Token Creator

1. **Go to**: https://www.solaneyes.com/token-creator/

2. **Connect Wallet**:
   - Click "Connect Wallet"
   - Select Phantom
   - Approve connection

3. **Switch to Devnet**:
   - Open Phantom wallet
   - Click Settings (⚙️)
   - Developer Settings
   - Toggle "Testnet Mode" ON
   - Select "Devnet" from network dropdown

4. **Create Token**:
   - Name: `IOIO`
   - Symbol: `IOIO`
   - Decimals: `2`
   - Initial Supply: `1000000`
   - Click "Create Token"

5. **Copy Address**:
   - After creation, token mint address appears
   - Example: `4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU`
   - **SAVE THIS**: This is your IOIO_TOKEN_MINT

### C. Configuration File

Create `payment/config.py`:

```python
# Paste your values here
PROGRAM_ID = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
IOIO_TOKEN_MINT = "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU"
GAME_WALLET = "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9"
RPC_URL = "https://api.devnet.solana.com"
GAME_COST = 1.0
```

## 🧪 Testing the System

### Test Checklist

- [ ] Smart contract deployed successfully
- [ ] IOIO token created
- [ ] Config file created with all 3 values
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test server running (`python test_payment.py`)
- [ ] Web interface accessible (http://127.0.0.1:5001)
- [ ] Configuration accepted in web interface
- [ ] QR code generated successfully
- [ ] Phantom wallet in Devnet mode
- [ ] Payment sent and confirmed
- [ ] Game start button enabled
- [ ] Score submitted successfully

### Expected Flow

```
1. Configure → ✅ "Configuration successful"
2. Generate QR → ✅ QR code appears
3. Scan & Pay → ⏳ "Waiting for payment..."
4. Payment Confirms → ✅ "Payment confirmed!"
5. Start Game → ✅ "Game started!"
6. Submit Score → ✅ "Score submitted: 100"
```

## 🐛 Troubleshooting

### "Adapter not configured"
- **Problem**: Missing Program ID, Token Mint, or Wallet
- **Solution**: Check all 3 values in config.py are filled

### "Payment timeout"
- **Problem**: Payment not detected within 5 minutes
- **Solution**: 
  - Check wallet is on Devnet
  - Verify token mint address is correct
  - Check you have Devnet SOL for fees

### "Build failed" in Solana Playground
- **Problem**: Code syntax error
- **Solution**: 
  - Copy code again carefully
  - Check no extra characters added
  - Verify Cargo.toml is correct

### "Token creation failed"
- **Problem**: Wallet not on Devnet or no SOL
- **Solution**:
  - Switch Phantom to Devnet
  - Get free Devnet SOL: https://faucet.solana.com/

## 📊 Smart Contract Functions

### `initialize()`
- Creates leaderboard account
- Called once when deploying

### `start_game_session(amount)`
- Creates new game session
- Transfers IOIO tokens from player to game vault
- Returns session ID

### `activate_game()`
- Marks game as started
- Called when physical button pressed

### `submit_score(score)`
- Records final score
- Updates leaderboard
- Sorts by highest score

### `get_leaderboard()`
- Returns top 100 scores
- Sorted by score (descending)

## 🔐 Security Notes

### Testnet Only
- This is configured for **Devnet** (testnet)
- Tokens have **NO REAL VALUE**
- Safe to test and experiment

### For Production (Mainnet)
- Change RPC_URL to mainnet
- Redeploy smart contract
- Create real IOIO token
- Add proper security audits
- Implement rate limiting
- Add transaction verification

## 📚 API Reference

### Python Adapter

```python
from solana_adapter import SolanaGameAdapter

# Initialize
adapter = SolanaGameAdapter(
    rpc_url="https://api.devnet.solana.com",
    program_id="YOUR_PROGRAM_ID",
    ioio_token_mint="YOUR_TOKEN_MINT",
    game_wallet="YOUR_WALLET"
)

# Generate payment QR
payment_url, session_id, qr_bytes = await adapter.generate_payment_request(
    amount=1.0,
    label="IOIO Game",
    message="Pay to play!"
)

# Check payment
paid = await adapter.check_payment(session_id)

# Monitor payment (blocking)
confirmed = await adapter.monitor_payment(session_id, timeout=300)

# Mark game started
adapter.mark_game_started(session_id)

# Submit score
adapter.submit_score(session_id, score=100)
```

## 🎮 Integration with Main App

After testing works, integrate into main Music-IO app:

1. Copy `solana_adapter.py` to `src/adapters/blockchain/`
2. Import in `application.py`
3. Add payment flow before game start
4. Submit scores to blockchain after game ends

See integration guide in main project docs.

## 📞 Support

If you encounter issues:

1. Check all 3 values are correct in config.py
2. Verify Phantom wallet is on Devnet
3. Confirm smart contract deployed successfully
4. Check test server logs for errors
5. Verify dependencies installed correctly

## 🎉 Success Criteria

You'll know it's working when:

- ✅ QR code generates without errors
- ✅ Phantom wallet can scan QR
- ✅ Payment transaction completes
- ✅ System detects payment automatically
- ✅ Game flow progresses correctly
- ✅ Score submission succeeds

## 📝 Next Steps

After successful testing:

1. **Test with real wallet**: Use Phantom on Devnet
2. **Test full flow**: Payment → Game → Score
3. **Verify leaderboard**: Check scores recorded
4. **Integrate**: Add to main Music-IO app
5. **Deploy to mainnet**: When ready for production

---

**🎊 You're ready to test! Follow the Quick Start Guide above.**
