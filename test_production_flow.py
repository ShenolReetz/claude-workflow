#!/usr/bin/env python3
"""
Test Production Flow Setup
==========================
Validates that all components are properly configured.
"""

import sys
import json
import asyncio
from pathlib import Path

# Add project to path
sys.path.append('/home/claude-workflow')

def test_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")
    
    errors = []
    
    # Test workflow runner
    try:
        from src.production_flow import LocalStorageWorkflowRunner, WorkflowPhase
        print("  ✅ Production flow imports")
    except ImportError as e:
        errors.append(f"Production flow: {e}")
    
    # Test MCP servers
    try:
        from mcp_servers.production_airtable_server import ProductionAirtableMCPServer
        print("  ✅ Airtable server imports")
    except ImportError as e:
        errors.append(f"Airtable server: {e}")
    
    try:
        from mcp_servers.production_credential_validation_server import ProductionCredentialValidationServerOptimized
        print("  ✅ Credential validation imports")
    except ImportError as e:
        errors.append(f"Credential validation: {e}")
    
    # Test MCP agents
    try:
        from src.mcp.production_imagen4_ultra_with_gpt4_vision import production_generate_images_with_imagen4_ultra
        print("  ✅ Image generation imports")
    except ImportError as e:
        errors.append(f"Image generation: {e}")
    
    try:
        from src.mcp.production_remotion_video_generator_strict import production_run_video_creation
        print("  ✅ Video generation imports")
    except ImportError as e:
        errors.append(f"Video generation: {e}")
    
    # Test utilities
    try:
        from src.utils.dual_storage_manager import get_storage_manager
        print("  ✅ Storage manager imports")
    except ImportError as e:
        errors.append(f"Storage manager: {e}")
    
    return errors

def test_config():
    """Test configuration file"""
    print("\n🔍 Testing configuration...")
    
    config_path = Path('/home/claude-workflow/config/api_keys.json')
    
    if not config_path.exists():
        return ["Config file not found"]
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_keys = [
            'openai_api_key',
            'airtable_api_key',
            'airtable_base_id',
            'elevenlabs_api_key',
            'scrapingdog_api_key',
            'wordpress_url',
            'wordpress_user',
            'wordpress_password'
        ]
        
        missing = [k for k in required_keys if k not in config]
        
        if missing:
            return [f"Missing config keys: {missing}"]
        
        print("  ✅ All required config keys present")
        return []
        
    except Exception as e:
        return [f"Config error: {e}"]

def test_directories():
    """Test required directories exist"""
    print("\n🔍 Testing directories...")
    
    required_dirs = [
        '/home/claude-workflow/media_storage',
        '/home/claude-workflow/src',
        '/home/claude-workflow/mcp_servers',
        '/home/claude-workflow/src/mcp',
        '/home/claude-workflow/src/utils',
        '/home/claude-workflow/config'
    ]
    
    errors = []
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✅ {dir_path}")
        else:
            errors.append(f"Missing directory: {dir_path}")
    
    return errors

async def test_workflow_phases():
    """Test workflow phase execution"""
    print("\n🔍 Testing workflow phases...")
    
    try:
        from src.production_flow import LocalStorageWorkflowRunner, WorkflowPhase
        
        runner = LocalStorageWorkflowRunner()
        
        # Check all phases have methods
        phase_count = len(WorkflowPhase)
        print(f"  ✅ {phase_count} phases defined")
        
        # Check phase dependencies
        deps_defined = len(runner.PHASE_DEPENDENCIES)
        print(f"  ✅ {deps_defined} phase dependencies defined")
        
        if phase_count != deps_defined:
            return [f"Phase count mismatch: {phase_count} phases, {deps_defined} dependencies"]
        
        return []
        
    except Exception as e:
        return [f"Workflow test error: {e}"]

def main():
    """Run all tests"""
    print("""
╔════════════════════════════════════════════════════════════╗
║          PRODUCTION FLOW VALIDATION TEST                   ║
╚════════════════════════════════════════════════════════════╝
""")
    
    all_errors = []
    
    # Test imports
    errors = test_imports()
    all_errors.extend(errors)
    
    # Test config
    errors = test_config()
    all_errors.extend(errors)
    
    # Test directories
    errors = test_directories()
    all_errors.extend(errors)
    
    # Test workflow phases
    errors = asyncio.run(test_workflow_phases())
    all_errors.extend(errors)
    
    # Summary
    print("\n" + "="*60)
    if all_errors:
        print("❌ VALIDATION FAILED")
        print("\nErrors found:")
        for error in all_errors:
            print(f"  - {error}")
    else:
        print("✅ ALL TESTS PASSED")
        print("\nProduction flow is ready to run!")
        print("\nTo start workflow:")
        print("  python3 /home/claude-workflow/run_local_storage.py")
    
    print("="*60)
    
    return 0 if not all_errors else 1

if __name__ == "__main__":
    sys.exit(main())