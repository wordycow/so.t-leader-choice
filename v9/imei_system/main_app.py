"""
IMEI Main Application (Flask-based)

Integrates:
- Persistent Memory Engine
- Dynamic Persona Engine
- Web Search Learning
- Trading Integration

Endpoints:
- POST /api/imei/chat - Chat with IMEI
- GET /api/imei/memories - Get user memories
- DELETE /api/imei/memory/:id - Delete memory
- GET /api/imei/export - Export state
- POST /api/imei/import - Import state
- GET /api/system/btc_regime - BTC regime status
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json
import sqlite3
import traceback
from datetime import datetime

# Add parent dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from imei_core.persistent_memory import PersistentMemoryEngine
from imei_core.dynamic_persona import DynamicPersonaEngine
from imei_core.web_search_learning import WebSearchLearning
from imei_core.trading_integration import TradingIntegration
from imei_core.emei_response_router import EmeiRouter

app = Flask(__name__)
CORS(app)

# Initialize engines
memory_engine = PersistentMemoryEngine(db_path="imei_memory.db")
persona_engine = DynamicPersonaEngine()
search_engine = WebSearchLearning()
trading_integration = TradingIntegration(dashboard_url="http://localhost:5000")

# Ollama configuration (성장형 AI를 위한 실제 LLM!)
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama.thetheunique.com")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_ENABLED = os.getenv("USE_OLLAMA", "true").lower() == "true"

# Initialize Ollama Router (v8 proven system)
emei_router = EmeiRouter(
    db_path="imei_memory.db",
    ollama_url=OLLAMA_URL,
    ollama_model=OLLAMA_MODEL
) if OLLAMA_ENABLED else None

print("========================================")
print("🚀 IMEI MAIN APP v3.0 with Ollama Router")
print("========================================")
print(f"📁 Memory Database: imei_memory.db")
print(f"🔗 Trading API: http://localhost:5000")
if OLLAMA_ENABLED and emei_router:
    print(f"🤖 Ollama Router: {OLLAMA_URL}")
    print(f"🧠 Model: {OLLAMA_MODEL}")
else:
    print("⚠️  Ollama Router: DISABLED (using mock responses)")
print("========================================")

# Default user ID (can be enhanced with auth later)
DEFAULT_USER_ID = "user_1"


# ========================================
# CHAT ENDPOINT
# ========================================

@app.route('/api/imei/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint with IMEI.
    
    Flow:
    1. Detect persona based on context
    2. Check memory trigger
    3. Check if web search needed (low RAG confidence)
    4. Generate response with persona style
    5. Save conversation
    6. Return response with metadata
    """
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', DEFAULT_USER_ID)
        include_trading_status = data.get('include_trading_status', False)
        
        if not user_message:
            return jsonify({
                'error': 'Message is required'
            }), 400
        
        response_data = {
            'user_message': user_message,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id
        }
        
        # Step 1: Detect context and select persona
        context_analysis = persona_engine.get_response_style(user_message)
        response_data['context'] = context_analysis
        
        # Step 2: Check memory trigger
        memory_triggered = memory_engine.check_memory_trigger(user_message)
        response_data['memory_triggered'] = memory_triggered
        
        # Step 3: Get trading status if requested
        trading_data = {}
        if include_trading_status:
            try:
                trading_data = {
                    'status': trading_integration.get_system_status(),
                    'top20': trading_integration.get_top20_candidates(),
                    'portfolio': trading_integration.get_portfolio()
                }
                response_data['trading_data'] = trading_data
            except Exception as e:
                response_data['trading_data_error'] = str(e)
        
        # Step 4: Generate response using Ollama Router or Mock
        if OLLAMA_ENABLED and emei_router:
            # Use v8 proven Ollama Router
            try:
                ollama_response = emei_router.chat(user_id=user_id, message=user_message)
                assistant_message = ollama_response.get('response', '')
                response_data['ollama_used'] = True
                response_data['ollama_learned'] = ollama_response.get('learned', False)
                response_data['response_time'] = ollama_response.get('response_time', 0)
            except Exception as e:
                # Fallback to mock on error
                assistant_message = generate_mock_response(user_message, context_analysis, trading_data)
                response_data['ollama_error'] = str(e)
                response_data['ollama_used'] = False
        else:
            # Mock response fallback
            assistant_message = generate_mock_response(user_message, context_analysis, trading_data)
            response_data['ollama_used'] = False
        
        # Step 6: Apply persona style (already in context_analysis from get_response_style)
        style_guide = context_analysis.get('style_guide', {})
        
        response_data['assistant_message'] = assistant_message
        response_data['response'] = assistant_message  # Add this for API compatibility
        response_data['persona'] = context_analysis.get('primary_persona', 'unknown')
        response_data['primary_persona'] = context_analysis.get('primary_persona', 'unknown')
        response_data['style_guide'] = style_guide
        
        # Step 7: Save conversation
        memory_engine.save_conversation(
            user_id=user_id,
            message=user_message,
            response=assistant_message
        )
        
        # Step 8: If memory triggered, save long-term memory
        memory_card = None
        if memory_triggered:
            memory_card = memory_engine.save_long_term_memory(
                user_id=user_id,
                message=user_message,
                response=assistant_message
            )
            response_data['memory_card'] = memory_card
        
        return jsonify(response_data), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


def generate_mock_response(user_message, context_analysis, trading_data):
    """
    Mock response generator (replace with real LLM in production).
    """
    persona = context_analysis.get('primary_persona', 'bold_leader')
    
    # Trading analysis
    if '차트' in user_message or '분석' in user_message:
        if trading_data:
            status = trading_data.get('status', {})
            mode = status.get('mode', 'unknown')
            return f"현재 시스템은 {mode} 모드입니다. 데이터를 분석한 결과를 알려드리겠습니다."
        return "차트 분석을 도와드리겠습니다. 데이터를 보면 흥미로운 패턴이 보이네요."
    
    # Emotional support
    if '힘들' in user_message or '어렵' in user_message:
        return "함께 할게요. 당신은 충분히 잘하고 있어요. 우리는 이 과정을 함께 헤쳐나갈 수 있습니다."
    
    # Decision making
    if '해야' in user_message or '할까' in user_message:
        return "제 판단으로는 명확한 방향이 있습니다. 확실한 건, 이렇게 하시는 게 좋습니다."
    
    # Default
    return f"({persona}) 잘 이해했어요. 함께 생각해보겠습니다."


# ========================================
# MEMORY ENDPOINTS
# ========================================

@app.route('/api/imei/memories', methods=['GET'])
def get_memories():
    """
    Get user's long-term memories.
    """
    try:
        user_id = request.args.get('user_id', DEFAULT_USER_ID)
        limit = int(request.args.get('limit', 50))
        
        memories = memory_engine.get_user_memories(user_id, limit=limit)
        
        return jsonify({
            'user_id': user_id,
            'count': len(memories),
            'memories': memories
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/imei/memory/<memory_id>', methods=['DELETE'])
def delete_memory(memory_id):
    """
    Delete a specific memory.
    """
    try:
        user_id = request.args.get('user_id', DEFAULT_USER_ID)
        
        memory_engine.delete_memory(user_id, memory_id)
        
        return jsonify({
            'success': True,
            'memory_id': memory_id,
            'message': 'Memory deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# EXPORT/IMPORT ENDPOINTS
# ========================================

@app.route('/api/imei/export', methods=['GET'])
def export_state():
    """
    Export agent state for cloning.
    """
    try:
        user_id = request.args.get('user_id', DEFAULT_USER_ID)
        include_user_memory = request.args.get('include_user_memory', 'false').lower() == 'true'
        
        export_data = memory_engine.export_state(
            user_id=user_id,
            include_user_memory=include_user_memory
        )
        
        return jsonify(export_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/imei/import', methods=['POST'])
def import_state():
    """
    Import agent state from another clone.
    """
    try:
        data = request.json
        user_id = data.get('user_id', DEFAULT_USER_ID)
        import_data = data.get('data')
        
        if not import_data:
            return jsonify({'error': 'Import data is required'}), 400
        
        result = memory_engine.import_state(import_data, user_id)
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# TRADING STATUS ENDPOINTS
# ========================================

@app.route('/api/system/btc_regime', methods=['GET'])
def get_btc_regime():
    """
    Get current BTC regime status.
    
    Returns:
    - regime: "normal" | "strong_bullish" | "full_downtrend"
    - indicators: H1, H4, stablecoin, dominance
    - block_new_entries: boolean
    - explanation: Human-readable explanation
    """
    try:
        # Call signal engine's BTC regime detector
        # (Mock for now, replace with real WS call or DB query)
        
        regime_data = {
            'regime': 'normal',
            'indicators': {
                'btc_h1_bullish': True,
                'btc_h4_bullish': True,
                'stablecoin_spike': False,
                'dominance_spike': False
            },
            'block_new_entries': False,
            'explanation': '비트코인 1시간 & 4시간 모두 상승세이며, 스테이블코인 및 도미넌스 급등이 없습니다. 정상 거래 가능합니다.',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(regime_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """
    Get comprehensive system status (alias for trading integration).
    """
    try:
        status = trading_integration.get_system_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/system/candidates', methods=['GET'])
def get_candidates():
    """
    Get TOP 20 candidates.
    """
    try:
        candidates = trading_integration.get_top20_candidates()
        return jsonify(candidates), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/system/portfolio', methods=['GET'])
def get_portfolio():
    """
    Get current portfolio.
    """
    try:
        portfolio = trading_integration.get_portfolio()
        return jsonify(portfolio), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========================================
# HEALTH CHECK
# ========================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'IMEI Main App',
        'version': '3.0',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# ========================================
# MAIN
# ========================================

if __name__ == '__main__':
    print("========================================")
    print("🚀 IMEI MAIN APP v3.0 with Ollama Router")
    print("========================================")
    print(f"📁 Memory Database: imei_memory.db")
    print(f"🔗 Trading API: http://localhost:5000")
    if OLLAMA_ENABLED and emei_router:
        print(f"🤖 Ollama Router: {OLLAMA_URL}")
        print(f"🧠 Model: {OLLAMA_MODEL}")
    else:
        print("⚠️  Ollama Router: DISABLED (using mock responses)")
    print("========================================")
    
    # Run on port 5001 (dashboard is on 5000)
    app.run(host='0.0.0.0', port=5001, debug=True)
