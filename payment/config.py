"""
Configuration for IOIO Payment System
"""

# ============================================================================
# SOLANA CONFIGURATION (Devnet)
# ============================================================================

# Program ID - Deployed smart contract
PROGRAM_ID = "E8v2TkXVJEbB7VKCMAVvJ1y2ULTrdqZ223guSpdtWtHf"

# IOIO Token Mint Address
IOIO_TOKEN_MINT = "6rRMCNUQzCSihFtbZCxjvmw2hUuFwuo7k5p3qXgd1qeA"

# Game Wallet Address
GAME_WALLET = "DyjsyTHsrRqEK7xRsp4VXmEFwpc6SNv6FZZjci5MEitC"

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
