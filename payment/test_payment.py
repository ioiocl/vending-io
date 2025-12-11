"""
Test Payment System - Standalone Flask App
Tests QR code generation and payment monitoring without integrating into main app
"""
import asyncio
import base64
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import logging
from solana_adapter import SolanaGameAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ioio-test-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Solana adapter (will be configured from web interface)
solana_adapter = None
current_session = None


@app.route('/')
def index():
    """Main test page"""
    return render_template('test_payment.html')


@app.route('/api/configure', methods=['POST'])
def configure():
    """Configure Solana adapter with blockchain details"""
    global solana_adapter
    
    try:
        data = request.json
        program_id = data.get('program_id')
        token_mint = data.get('token_mint')
        game_wallet = data.get('game_wallet')
        
        if not all([program_id, token_mint, game_wallet]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Initialize adapter
        solana_adapter = SolanaGameAdapter(
            rpc_url="https://api.devnet.solana.com",
            program_id=program_id,
            ioio_token_mint=token_mint,
            game_wallet=game_wallet
        )
        
        logger.info("✅ Solana adapter configured")
        
        return jsonify({
            'success': True,
            'message': 'Adapter configured successfully',
            'rpc_url': solana_adapter.rpc_url
        })
        
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate_payment', methods=['POST'])
def generate_payment():
    """Generate payment QR code"""
    global solana_adapter, current_session
    
    if not solana_adapter or not solana_adapter.is_configured():
        return jsonify({
            'success': False,
            'error': 'Adapter not configured. Configure first.'
        }), 400
    
    try:
        data = request.json
        amount = float(data.get('amount', 0.001))  # Default to 0.001 SOL for testing
        
        # Generate payment request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        payment_url, session_id, qr_bytes = loop.run_until_complete(
            solana_adapter.generate_payment_request(
                amount=amount,
                label="IOIO Game Test",
                message="Test payment - Devnet"
            )
        )
        
        current_session = session_id
        
        # Convert QR to base64 for web display
        qr_base64 = base64.b64encode(qr_bytes).decode('utf-8')
        
        logger.info(f"✅ Payment request generated: {session_id}")
        
        # Start monitoring payment in background
        socketio.start_background_task(monitor_payment, session_id)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'payment_url': payment_url,
            'qr_code': f'data:image/png;base64,{qr_base64}',
            'amount': amount
        })
        
    except Exception as e:
        logger.error(f"Payment generation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def monitor_payment(session_id):
    """Background task to monitor payment"""
    logger.info(f"🔍 Monitoring payment for session: {session_id}")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def check_loop():
        timeout = 300  # 5 minutes
        elapsed = 0
        check_interval = 2
        
        while elapsed < timeout:
            paid = await solana_adapter.check_payment(session_id)
            
            if paid:
                logger.info(f"✅ Payment confirmed: {session_id}")
                
                # Notify frontend
                socketio.emit('payment_confirmed', {
                    'session_id': session_id,
                    'timestamp': solana_adapter.active_sessions[session_id]['timestamp']
                })
                
                return True
            
            await asyncio.sleep(check_interval)
            elapsed += check_interval
            
            # Send progress update every 10 seconds
            if elapsed % 10 == 0:
                socketio.emit('payment_status', {
                    'session_id': session_id,
                    'elapsed': elapsed,
                    'status': 'waiting'
                })
        
        # Timeout
        logger.warning(f"⏱️ Payment timeout: {session_id}")
        socketio.emit('payment_timeout', {
            'session_id': session_id
        })
        
        return False
    
    loop.run_until_complete(check_loop())


@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session information"""
    if not solana_adapter:
        return jsonify({
            'success': False,
            'error': 'Adapter not initialized'
        }), 400
    
    session_info = solana_adapter.get_session_info(session_id)
    
    if not session_info:
        return jsonify({
            'success': False,
            'error': 'Session not found'
        }), 404
    
    return jsonify({
        'success': True,
        'session': session_info
    })


@app.route('/api/start_game/<session_id>', methods=['POST'])
def start_game(session_id):
    """Mark game as started (simulates button press)"""
    if not solana_adapter:
        return jsonify({
            'success': False,
            'error': 'Adapter not initialized'
        }), 400
    
    success = solana_adapter.mark_game_started(session_id)
    
    if success:
        logger.info(f"🎮 Game started: {session_id}")
        return jsonify({
            'success': True,
            'message': 'Game started'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Could not start game'
        }), 400


@app.route('/api/submit_score/<session_id>', methods=['POST'])
def submit_score(session_id):
    """Submit game score"""
    if not solana_adapter:
        return jsonify({
            'success': False,
            'error': 'Adapter not initialized'
        }), 400
    
    try:
        data = request.json
        score = int(data.get('score', 0))
        
        success = solana_adapter.submit_score(session_id, score)
        
        if success:
            logger.info(f"📊 Score submitted: {score} for session {session_id}")
            return jsonify({
                'success': True,
                'score': score
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not submit score'
            }), 400
            
    except Exception as e:
        logger.error(f"Score submission error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('connected', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')


if __name__ == '__main__':
    print("="*60)
    print("🧪 IOIO Payment Test Server")
    print("="*60)
    print("\n📍 Open your browser to: http://127.0.0.1:5001")
    print("\n⚠️  Make sure to configure with your Solana details first!")
    print("\n" + "="*60 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)
