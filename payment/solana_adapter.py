"""
Solana Payment Adapter for IOIO Game
Handles blockchain interactions, payment verification, and game session management
"""
import asyncio
import base64
import json
import logging
from typing import Optional, Dict, Callable
from datetime import datetime

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts
import qrcode
from io import BytesIO
import base58

logger = logging.getLogger(__name__)


class SolanaGameAdapter:
    """
    Adapter for Solana blockchain integration
    Handles payment verification and game session management
    """
    
    def __init__(
        self,
        rpc_url: str = "https://api.devnet.solana.com",
        program_id: Optional[str] = None,
        ioio_token_mint: Optional[str] = None,
        game_wallet: Optional[str] = None
    ):
        """
        Initialize Solana adapter
        
        Args:
            rpc_url: Solana RPC endpoint (default: Devnet)
            program_id: Deployed program ID (get from Solana Playground)
            ioio_token_mint: IOIO token mint address
            game_wallet: Game's receiving wallet address
        """
        self.rpc_url = rpc_url
        self.client = AsyncClient(rpc_url)
        self.program_id = Pubkey.from_string(program_id) if program_id else None
        self.ioio_token_mint = Pubkey.from_string(ioio_token_mint) if ioio_token_mint else None
        self.game_wallet = Pubkey.from_string(game_wallet) if game_wallet else None
        
        # Active game sessions
        self.active_sessions: Dict[str, Dict] = {}
        
        # Callbacks
        self.payment_callback: Optional[Callable] = None
        
        logger.info(f"Solana adapter initialized (RPC: {rpc_url})")
        logger.info(f"Program ID: {program_id}")
        logger.info(f"IOIO Token: {ioio_token_mint}")
    
    def is_configured(self) -> bool:
        """Check if adapter is fully configured"""
        return all([
            self.program_id is not None,
            self.ioio_token_mint is not None,
            self.game_wallet is not None
        ])
    
    async def generate_payment_request(
        self,
        amount: float = 1.0,
        label: str = "IOIO Game",
        message: str = "Pay to play!"
    ) -> tuple[str, str, bytes]:
        """
        Generate Solana Pay payment request with QR code
        
        Args:
            amount: Amount in IOIO tokens
            label: Payment label
            message: Payment message
        
        Returns:
            Tuple of (payment_url, session_id, qr_code_bytes)
        """
        if not self.is_configured():
            raise ValueError("Adapter not configured. Set program_id, ioio_token_mint, and game_wallet")
        
        # Generate unique reference for this payment
        reference_keypair = Keypair()
        reference = str(reference_keypair.pubkey())
        session_id = reference
        
        # Create Solana Pay URL for SOL (native token)
        # Format: solana:<recipient>?amount=<amount>&reference=<ref>&label=<label>&message=<msg>
        from urllib.parse import quote
        
        payment_url = (
            f"solana:{self.game_wallet}?"
            f"amount={amount}&"
            f"reference={reference}&"
            f"label={quote(label)}&"
            f"message={quote(message)}"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(payment_url)
        qr.make(fit=True)
        
        # Convert to bytes
        img = qr.make_image(fill_color="black", back_color="white")
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        qr_bytes = img_bytes.getvalue()
        
        # Store session
        self.active_sessions[session_id] = {
            'reference': reference,
            'amount': amount,
            'timestamp': datetime.now().isoformat(),
            'paid': False,
            'game_started': False,
            'score': None
        }
        
        logger.info(f"Payment request generated: {session_id}")
        logger.info(f"Amount: {amount} IOIO")
        logger.info(f"Reference: {reference}")
        
        return payment_url, session_id, qr_bytes
    
    async def check_payment(self, session_id: str) -> bool:
        """
        Check if payment has been received for a session
        
        Args:
            session_id: Session ID (reference pubkey)
        
        Returns:
            True if payment confirmed, False otherwise
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Session not found: {session_id}")
            return False
        
        session = self.active_sessions[session_id]
        
        # If already paid, return True
        if session['paid']:
            return True
        
        try:
            # Get signatures for the reference address
            reference_pubkey = Pubkey.from_string(session['reference'])
            
            response = await self.client.get_signatures_for_address(
                reference_pubkey,
                commitment=Confirmed
            )
            
            if response.value:
                # Payment found!
                session['paid'] = True
                session['payment_signature'] = str(response.value[0].signature)
                
                logger.info(f"✅ Payment confirmed for session: {session_id}")
                logger.info(f"Signature: {session['payment_signature']}")
                
                # Call payment callback if registered
                if self.payment_callback:
                    await self.payment_callback(session_id, session)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking payment: {e}")
            return False
    
    async def monitor_payment(
        self,
        session_id: str,
        timeout: int = 300,
        check_interval: int = 2
    ) -> bool:
        """
        Monitor payment until confirmed or timeout
        
        Args:
            session_id: Session ID to monitor
            timeout: Timeout in seconds (default: 5 minutes)
            check_interval: Check interval in seconds (default: 2 seconds)
        
        Returns:
            True if payment confirmed, False if timeout
        """
        logger.info(f"Monitoring payment for session: {session_id}")
        logger.info(f"Timeout: {timeout}s, Check interval: {check_interval}s")
        
        elapsed = 0
        while elapsed < timeout:
            paid = await self.check_payment(session_id)
            
            if paid:
                return True
            
            await asyncio.sleep(check_interval)
            elapsed += check_interval
            
            if elapsed % 10 == 0:  # Log every 10 seconds
                logger.info(f"Still waiting... ({elapsed}s elapsed)")
        
        logger.warning(f"Payment timeout for session: {session_id}")
        return False
    
    def mark_game_started(self, session_id: str) -> bool:
        """Mark game as started for a session"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        if not session['paid']:
            logger.warning(f"Cannot start game - payment not confirmed: {session_id}")
            return False
        
        session['game_started'] = True
        logger.info(f"Game started for session: {session_id}")
        return True
    
    def submit_score(self, session_id: str, score: int) -> bool:
        """Submit final score for a session"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        if not session['game_started']:
            logger.warning(f"Cannot submit score - game not started: {session_id}")
            return False
        
        session['score'] = score
        session['completed'] = True
        logger.info(f"Score submitted for session {session_id}: {score}")
        return True
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        return self.active_sessions.get(session_id)
    
    def register_payment_callback(self, callback: Callable):
        """Register callback to be called when payment is confirmed"""
        self.payment_callback = callback
        logger.info("Payment callback registered")
    
    async def close(self):
        """Close the adapter and cleanup"""
        await self.client.close()
        logger.info("Solana adapter closed")


# Example usage and testing
async def test_adapter():
    """Test the Solana adapter"""
    print("="*60)
    print("🧪 Testing Solana Payment Adapter")
    print("="*60)
    
    # Initialize adapter (without config for testing)
    adapter = SolanaGameAdapter()
    
    print(f"\n✅ Adapter initialized")
    print(f"RPC URL: {adapter.rpc_url}")
    print(f"Configured: {adapter.is_configured()}")
    
    # Test with mock configuration
    adapter.program_id = Pubkey.from_string("11111111111111111111111111111111")
    adapter.ioio_token_mint = Pubkey.from_string("11111111111111111111111111111111")
    adapter.game_wallet = Pubkey.from_string("11111111111111111111111111111111")
    
    print(f"\n✅ Mock configuration set")
    print(f"Configured: {adapter.is_configured()}")
    
    # Generate payment request
    try:
        payment_url, session_id, qr_bytes = await adapter.generate_payment_request(
            amount=1.0,
            label="IOIO Game Test",
            message="Test payment"
        )
        
        print(f"\n✅ Payment request generated")
        print(f"Session ID: {session_id}")
        print(f"Payment URL: {payment_url[:80]}...")
        print(f"QR Code size: {len(qr_bytes)} bytes")
        
        # Get session info
        session_info = adapter.get_session_info(session_id)
        print(f"\n📊 Session Info:")
        print(f"  Amount: {session_info['amount']} IOIO")
        print(f"  Paid: {session_info['paid']}")
        print(f"  Game Started: {session_info['game_started']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    await adapter.close()
    print(f"\n✅ Test complete")


if __name__ == "__main__":
    asyncio.run(test_adapter())
