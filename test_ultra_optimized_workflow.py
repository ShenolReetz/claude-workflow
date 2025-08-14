#!/usr/bin/env python3
"""
Test Suite for Ultra-Optimized Workflow
========================================

Tests all optimization features:
1. Parallel credential validation
2. Redis caching
3. Circuit breakers
4. Parallel phase execution
5. Performance benchmarks
"""

import asyncio
import json
import time
import sys
from datetime import datetime

sys.path.append('/home/claude-workflow')

from src.utils.cache_manager import get_cache_manager, CacheManager
from src.utils.circuit_breaker import get_circuit_breaker_manager, CircuitOpenError
from mcp_servers.production_credential_validation_server_optimized import ProductionCredentialValidationServerOptimized

async def test_parallel_credential_validation():
    """Test that credential validation runs in parallel"""
    print("\n🔍 Testing Parallel Credential Validation...")
    print("-" * 50)
    
    validator = ProductionCredentialValidationServerOptimized()
    
    # Time the validation
    start = time.time()
    result = await validator.validate_all_credentials()
    elapsed = time.time() - start
    
    print(f"✅ Validation completed in {elapsed:.2f} seconds")
    print(f"📊 Health Score: {result['health_score']}/100")
    print(f"⚡ Parallel speedup: {result.get('parallel_speedup', 'N/A')}")
    print(f"🔍 Services validated: {result['services_validated']}")
    
    # Check that it's actually fast (should be under 30 seconds)
    if elapsed < 30:
        print("✅ PASS: Validation completed in under 30 seconds")
    else:
        print(f"❌ FAIL: Validation took {elapsed:.2f} seconds (expected < 30s)")
    
    return elapsed < 30

async def test_redis_caching():
    """Test Redis caching functionality"""
    print("\n💾 Testing Redis Caching...")
    print("-" * 50)
    
    cache = await get_cache_manager()
    
    # Test set and get
    test_key = "test_key"
    test_value = {"data": "test_value", "timestamp": datetime.now().isoformat()}
    
    # Set value
    await cache.set(CacheManager.CATEGORY_PRODUCTS, test_key, test_value, ttl=60)
    print("✅ Value cached successfully")
    
    # Get value (should be cache hit)
    start = time.time()
    retrieved = await cache.get(CacheManager.CATEGORY_PRODUCTS, test_key)
    elapsed = time.time() - start
    
    if retrieved == test_value:
        print(f"✅ PASS: Cache hit successful (retrieved in {elapsed*1000:.2f}ms)")
    else:
        print("❌ FAIL: Cache retrieval failed")
        return False
    
    # Test cache stats
    stats = await cache.get_stats()
    print(f"📊 Cache stats: Hit rate={stats['hit_rate']}, Total hits={stats['hits']}")
    
    # Test category invalidation
    await cache.invalidate_category(CacheManager.CATEGORY_PRODUCTS)
    retrieved_after = await cache.get(CacheManager.CATEGORY_PRODUCTS, test_key)
    
    if retrieved_after is None:
        print("✅ PASS: Category invalidation working")
    else:
        print("❌ FAIL: Category invalidation failed")
        return False
    
    return True

async def test_circuit_breakers():
    """Test circuit breaker functionality"""
    print("\n⚡ Testing Circuit Breakers...")
    print("-" * 50)
    
    manager = get_circuit_breaker_manager()
    
    # Test with a failing function
    failure_count = 0
    async def failing_function():
        nonlocal failure_count
        failure_count += 1
        raise Exception("Simulated failure")
    
    # Trigger circuit breaker
    breaker = manager.get_breaker('test_service')
    breaker.failure_threshold = 3  # Open after 3 failures
    
    # Attempt calls until circuit opens
    for i in range(5):
        try:
            await breaker.call(failing_function)
        except CircuitOpenError:
            print(f"✅ Circuit opened after {failure_count} failures (threshold: 3)")
            break
        except Exception:
            continue
    
    # Check circuit state
    status = breaker.get_status()
    if status['state'] == 'open':
        print("✅ PASS: Circuit breaker opened correctly")
    else:
        print(f"❌ FAIL: Circuit in wrong state: {status['state']}")
        return False
    
    # Test that circuit blocks calls when open
    try:
        await breaker.call(failing_function)
        print("❌ FAIL: Circuit should block calls when open")
        return False
    except CircuitOpenError:
        print("✅ PASS: Circuit blocks calls when open")
    
    # Reset for cleanup
    breaker.reset()
    
    return True

async def test_workflow_phases():
    """Test workflow phase dependencies and parallel execution"""
    print("\n🔄 Testing Workflow Phase Management...")
    print("-" * 50)
    
    from src.production_workflow_runner_ultra_optimized import WorkflowPhase, UltraOptimizedWorkflowRunner
    
    runner = UltraOptimizedWorkflowRunner()
    
    # Test dependency checking
    runner.completed_phases = {WorkflowPhase.INIT, WorkflowPhase.CREDENTIALS}
    
    # FETCH_TITLE should be executable (deps: CREDENTIALS)
    can_fetch = await runner.can_execute_phase(WorkflowPhase.FETCH_TITLE)
    if can_fetch:
        print("✅ PASS: Dependency checking working")
    else:
        print("❌ FAIL: Should be able to execute FETCH_TITLE")
        return False
    
    # CREATE_VIDEO should NOT be executable (missing deps)
    can_video = await runner.can_execute_phase(WorkflowPhase.CREATE_VIDEO)
    if not can_video:
        print("✅ PASS: Correctly blocked phase with missing dependencies")
    else:
        print("❌ FAIL: Should NOT be able to execute CREATE_VIDEO")
        return False
    
    # Test parallel phase identification
    runner.completed_phases = {
        WorkflowPhase.INIT,
        WorkflowPhase.CREDENTIALS,
        WorkflowPhase.FETCH_TITLE,
        WorkflowPhase.SCRAPE_PRODUCTS,
        WorkflowPhase.EXTRACT_CATEGORY,
        WorkflowPhase.VALIDATE_PRODUCTS,
        WorkflowPhase.SAVE_PRODUCTS,
        WorkflowPhase.GENERATE_CONTENT,
        WorkflowPhase.GENERATE_SCRIPTS
    }
    
    # These should be executable in parallel
    parallel_phases = [
        WorkflowPhase.GENERATE_VOICE,
        WorkflowPhase.GENERATE_INTRO_IMAGE,
        WorkflowPhase.GENERATE_OUTRO_IMAGE
    ]
    
    can_run_parallel = all([
        await runner.can_execute_phase(phase) for phase in parallel_phases
    ])
    
    if can_run_parallel:
        print("✅ PASS: Parallel phases correctly identified")
    else:
        print("❌ FAIL: Should be able to run voice/images in parallel")
        return False
    
    return True

async def benchmark_performance():
    """Benchmark key performance metrics"""
    print("\n📊 Performance Benchmarks...")
    print("-" * 50)
    
    results = {}
    
    # Benchmark cache operations
    cache = await get_cache_manager()
    
    # Write benchmark
    start = time.time()
    for i in range(100):
        await cache.set(CacheManager.CATEGORY_PRODUCTS, f"bench_{i}", {"value": i})
    write_time = time.time() - start
    results['cache_writes_per_sec'] = 100 / write_time
    
    # Read benchmark
    start = time.time()
    for i in range(100):
        await cache.get(CacheManager.CATEGORY_PRODUCTS, f"bench_{i}")
    read_time = time.time() - start
    results['cache_reads_per_sec'] = 100 / read_time
    
    # Clean up
    await cache.invalidate_category(CacheManager.CATEGORY_PRODUCTS)
    
    print(f"💾 Cache Performance:")
    print(f"   Writes: {results['cache_writes_per_sec']:.0f} ops/sec")
    print(f"   Reads: {results['cache_reads_per_sec']:.0f} ops/sec")
    
    # Benchmark circuit breaker overhead
    manager = get_circuit_breaker_manager()
    breaker = manager.get_breaker('benchmark')
    
    async def fast_function():
        return "success"
    
    # Measure overhead
    start = time.time()
    for _ in range(1000):
        await breaker.call(fast_function)
    cb_time = time.time() - start
    
    # Direct calls for comparison
    start = time.time()
    for _ in range(1000):
        await fast_function()
    direct_time = time.time() - start
    
    overhead_percent = ((cb_time - direct_time) / direct_time) * 100
    
    print(f"\n⚡ Circuit Breaker Overhead:")
    print(f"   Direct calls: {direct_time*1000:.2f}ms for 1000 calls")
    print(f"   With circuit breaker: {cb_time*1000:.2f}ms for 1000 calls")
    print(f"   Overhead: {overhead_percent:.1f}%")
    
    return results

async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 ULTRA-OPTIMIZED WORKFLOW TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Parallel Credential Validation", test_parallel_credential_validation),
        ("Redis Caching", test_redis_caching),
        ("Circuit Breakers", test_circuit_breakers),
        ("Workflow Phases", test_workflow_phases),
        ("Performance Benchmarks", benchmark_performance)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result not in [False, None]:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Workflow optimizations verified.")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Review the output above.")

if __name__ == "__main__":
    asyncio.run(main())