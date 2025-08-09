#!/usr/bin/env python3
"""
Test script to verify credential validation fixes
"""

import asyncio
import sys
import time
sys.path.append('/home/claude-workflow')

from mcp_servers.Production_credential_validation_server import ProductionCredentialValidationServer

async def test_validation():
    """Test the credential validation with timeout fixes"""
    print("🧪 Testing Credential Validation Fixes")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Initialize validation server
        print("🔧 Initializing validation server...")
        validator = ProductionCredentialValidationServer()
        
        # Run validation with timeout
        print("🔍 Starting validation test...")
        validation_report = await asyncio.wait_for(
            validator.validate_all_credentials(),
            timeout=300  # 5 minute timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Validation completed successfully!")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Health Score: {validation_report['health_score']}/100")
        print(f"🚀 Can Proceed: {validation_report['can_proceed']}")
        
        if validation_report.get('critical_failures'):
            print(f"❌ Critical Failures: {len(validation_report['critical_failures'])}")
        if validation_report.get('warnings'):
            print(f"⚠️  Warnings: {len(validation_report['warnings'])}")
            
        return True
        
    except asyncio.TimeoutError:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ TIMEOUT: Validation timed out after {duration:.2f} seconds")
        return False
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ ERROR: Validation failed after {duration:.2f} seconds")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Production Credential Validation Fix Test")
    result = asyncio.run(test_validation())
    
    if result:
        print("\n✅ TEST PASSED - Validation completed without hanging!")
        exit(0)
    else:
        print("\n❌ TEST FAILED - Validation still has issues!")
        exit(1)