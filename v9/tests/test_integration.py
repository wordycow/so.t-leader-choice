"""
Integration Tests for IMEI v3.0

Tests:
1. Persona adaptation
2. Memory triggers and saving
3. Export/Import state
4. Sensitive data redaction
5. Web search learning
6. Trading integration
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from imei_core.persistent_memory import PersistentMemoryEngine
from imei_core.dynamic_persona import DynamicPersonaEngine
from imei_core.web_search_learning import WebSearchLearning
from imei_core.trading_integration import TradingIntegration
import json
from datetime import datetime


def print_test_header(test_name):
    print("\n" + "="*60)
    print(f"TEST: {test_name}")
    print("="*60)


def test_persona_adaptation():
    """Test persona detection and adaptation."""
    print_test_header("Persona Adaptation")
    
    persona_engine = DynamicPersonaEngine()
    
    test_cases = [
        ("비트코인 차트를 분석해줘", "analytical_strategist"),
        ("요즘 트레이딩이 너무 힘들어", "warm_support"),
        ("지금 매수해야 할까?", "bold_leader"),
        ("오늘 좋은 거래를 했어", "loyal_companion")
    ]
    
    passed = 0
    failed = 0
    
    for message, expected_persona in test_cases:
        style = persona_engine.get_response_style(message)
        detected = style['primary_persona']
        
        if expected_persona is None:
            print(f"⏭️  SKIP: '{message}' → {detected} (context-dependent)")
            continue
        
        if detected == expected_persona:
            print(f"✅ PASS: '{message}' → {detected}")
            passed += 1
        else:
            print(f"❌ FAIL: '{message}' → {detected} (expected {expected_persona})")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_memory_triggers():
    """Test memory trigger detection and saving."""
    print_test_header("Memory Triggers and Saving")
    
    memory_engine = PersistentMemoryEngine(db_path=":memory:")
    # Force re-initialization to ensure tables exist
    memory_engine._init_db()
    
    test_cases = [
        ("학습해: 비트코인은 1시간봉을 중요하게 봐야 해", True),
        ("저장해줘: 내 손절은 -2%로 설정했어", True),
        ("비트코인 가격이 어떻게 되나요?", False),
        ("알지? 우리가 어제 이야기한 전략", True)
    ]
    
    passed = 0
    failed = 0
    
    for message, should_trigger in test_cases:
        triggered = memory_engine.check_memory_trigger(message)
        
        if triggered == should_trigger:
            print(f"✅ PASS: '{message}' → {'Triggered' if triggered else 'Not triggered'}")
            passed += 1
        else:
            print(f"❌ FAIL: '{message}' → {'Triggered' if triggered else 'Not triggered'} (expected {'Triggered' if should_trigger else 'Not triggered'})")
            failed += 1
    
    # Test actual saving
    user_id = "test_user"
    memory_card = memory_engine.save_long_term_memory(
        user_id=user_id,
        message="학습해: RSI 30 이하면 매수 신호",
        response="네, 기억하겠습니다. RSI 30 이하는 매수 신호로 저장했습니다."
    )
    
    if memory_card and 'memory_id' in memory_card:
        print(f"✅ PASS: Memory saved with ID {memory_card['memory_id']}")
        passed += 1
    else:
        print(f"❌ FAIL: Memory save failed")
        failed += 1
    
    # Retrieve memories
    memories = memory_engine.get_user_memories(user_id, limit=10)
    if len(memories) > 0:
        print(f"✅ PASS: Retrieved {len(memories)} memories")
        passed += 1
    else:
        print(f"❌ FAIL: No memories retrieved")
        failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_sensitive_redaction():
    """Test sensitive data redaction."""
    print_test_header("Sensitive Data Redaction")
    
    memory_engine = PersistentMemoryEngine(db_path=":memory:")
    
    test_cases = [
        ("내 OTP는 123456입니다", "[OTP_REDACTED]"),
        ("API key: sk_abcdef1234567890abcdef1234567890", "[API_KEY_REDACTED]"),
        ("지갑 주소: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", "[WALLET_REDACTED]"),
        ("카드 번호 1234-5678-9012-3456", "[CARD_REDACTED]"),
        ("주민번호 123456-1234567", "[ID_REDACTED]"),
        ("password: mySecretPass123", "[REDACTED]")
    ]
    
    passed = 0
    failed = 0
    
    for text, expected_redaction in test_cases:
        redacted = memory_engine.redact_sensitive_data(text)
        
        if expected_redaction in redacted:
            print(f"✅ PASS: Redacted correctly")
            print(f"   Original: {text}")
            print(f"   Redacted: {redacted}")
            passed += 1
        else:
            print(f"❌ FAIL: Redaction incomplete")
            print(f"   Original: {text}")
            print(f"   Redacted: {redacted}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_export_import():
    """Test export/import state."""
    print_test_header("Export/Import State")
    
    # Create source memory engine
    source_memory = PersistentMemoryEngine(db_path=":memory:")
    
    # Add some test data
    source_memory.save_long_term_memory(
        user_id="user_1",
        message="학습해: BTC 1시간봉 중요",
        response="저장했습니다."
    )
    
    source_memory.save_to_knowledge_pool(
        question="RSI란?",
        answer="Relative Strength Index, 과매수/과매도 지표",
        source="manual"
    )
    
    # Export
    export_data = source_memory.export_state(user_id="user_1", include_user_memory=True)
    
    passed = 0
    failed = 0
    
    if 'version' in export_data and export_data['version'] == '3.0':
        print("✅ PASS: Export has correct version")
        passed += 1
    else:
        print("❌ FAIL: Export version incorrect")
        failed += 1
    
    if 'knowledge_pool' in export_data and len(export_data['knowledge_pool']) > 0:
        print(f"✅ PASS: Knowledge pool exported ({len(export_data['knowledge_pool'])} items)")
        passed += 1
    else:
        print("❌ FAIL: Knowledge pool not exported")
        failed += 1
    
    if 'user_memory' in export_data and len(export_data['user_memory']) > 0:
        print(f"✅ PASS: User memory exported ({len(export_data['user_memory'])} items)")
        passed += 1
    else:
        print("❌ FAIL: User memory not exported")
        failed += 1
    
    # Import to new memory engine
    target_memory = PersistentMemoryEngine(db_path=":memory:")
    result = target_memory.import_state(export_data, "user_2")
    
    if result['knowledge_imported'] > 0:
        print(f"✅ PASS: Knowledge imported ({result['knowledge_imported']} items)")
        passed += 1
    else:
        print("❌ FAIL: Knowledge import failed")
        failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_web_search_learning():
    """Test web search learning pipeline."""
    print_test_header("Web Search Learning")
    
    import tempfile
    import os
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    search_engine = WebSearchLearning()
    memory_engine = PersistentMemoryEngine(db_path=temp_db.name)
    
    passed = 0
    failed = 0
    
    # Test confidence threshold
    if not search_engine.should_search(0.8):
        print("✅ PASS: High confidence (0.8) → No search needed")
        passed += 1
    else:
        print("❌ FAIL: High confidence should not trigger search")
        failed += 1
    
    if search_engine.should_search(0.5):
        print("✅ PASS: Low confidence (0.5) → Search triggered")
        passed += 1
    else:
        print("❌ FAIL: Low confidence should trigger search")
        failed += 1
    
    # Test search (mock)
    query = "What is RSI indicator?"
    result = search_engine.learn_from_search(query, memory_engine)
    
    if 'summary' in result:
        print(f"✅ PASS: Search result summary generated")
        print(f"   Query: {query}")
        print(f"   Summary: {result['summary'][:100]}...")
        passed += 1
    else:
        print("❌ FAIL: No summary in search result")
        failed += 1
    
    if 'saved_to_knowledge' in result and result['saved_to_knowledge']:
        print("✅ PASS: Search result saved to knowledge pool")
        passed += 1
    else:
        print("❌ FAIL: Search result not saved")
        failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_trading_integration():
    """Test trading integration."""
    print_test_header("Trading Integration")
    
    # This will fail if trading API is not running, but we test the structure
    trading_integration = TradingIntegration(base_url="http://localhost:5000")
    
    passed = 0
    failed = 0
    
    # Test entry/exit explanations
    entry_explanation = trading_integration.explain_entry(
        strategy="ULTRA_SCALP_V2_1",
        entry_reason="BOLLINGER_BREAK"
    )
    
    if "볼린저" in entry_explanation or "하단" in entry_explanation:
        print(f"✅ PASS: Entry explanation generated")
        print(f"   {entry_explanation}")
        passed += 1
    else:
        print("❌ FAIL: Entry explanation incomplete")
        failed += 1
    
    exit_explanation = trading_integration.explain_exit(
        exit_reason="PARTIAL_3",
        exit_pct=30
    )
    
    if "3%" in exit_explanation or "30%" in exit_explanation:
        print(f"✅ PASS: Exit explanation generated")
        print(f"   {exit_explanation}")
        passed += 1
    else:
        print("❌ FAIL: Exit explanation incomplete")
        failed += 1
    
    print(f"\nNote: API calls skipped (requires running trading system)")
    print(f"Results: {passed} passed, {failed} failed (API tests skipped)")
    return failed == 0


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("IMEI v3.0 INTEGRATION TESTS")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "Persona Adaptation": test_persona_adaptation(),
        "Memory Triggers": test_memory_triggers(),
        "Sensitive Redaction": test_sensitive_redaction(),
        "Export/Import": test_export_import(),
        "Web Search Learning": test_web_search_learning(),
        "Trading Integration": test_trading_integration()
    }
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {failed} TESTS FAILED")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
= run_all_tests()
    sys.exit(exit_code)
