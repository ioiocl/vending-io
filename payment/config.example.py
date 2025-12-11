"""
Configuration Template for IOIO Payment System
Copy this to config.py and fill in your values from Solana Playground
"""

# ============================================================================
# SOLANA CONFIGURATION (Devnet)
# ============================================================================

# Program ID - Get this after deploying smart contract in Solana Playground
# Example: "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
PROGRAM_ID = "PASTE_YOUR_PROGRAM_ID_HERE"

# IOIO Token Mint Address - Get this after creating token
# Example: "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU"
IOIO_TOKEN_MINT = "PASTE_YOUR_TOKEN_MINT_HERE"

# Game Wallet Address - Your wallet from Solana Playground
# Example: "5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9"
GAME_WALLET = "PASTE_YOUR_WALLET_ADDRESS_HERE"

# RPC URL (Devnet - free)
RPC_URL = "https://api.devnet.solana.com"

# ============================================================================
# GAME CONFIGURATION
# ============================================================================

# Cost to play (in IOIO tokens)
GAME_COST = 1.0

# Payment timeout (seconds)
PAYMENT_TIMEOUT = 300  # 5 minutes

# Payment check interval (seconds)
PAYMENT_CHECK_INTERVAL = 2

# ============================================================================
# INSTRUCTIONS
# ============================================================================
# 
# 1. Deploy smart contract in Solana Playground
#    - Copy the Program ID that appears after deployment
#    - Paste it in PROGRAM_ID above
#
# 2. Create IOIO token
#    - Use Token Creator or CLI
#    - Copy the Token Mint address
#    - Paste it in IOIO_TOKEN_MINT above
#
# 3. Get your wallet address
#    - From Solana Playground wallet
#    - Paste it in GAME_WALLET above
#
# 4. Save this file as config.py (remove .example)
#
# 5. Run: python test_payment.py
#
# ============================================================================
