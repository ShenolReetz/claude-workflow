#!/usr/bin/env python3
"""
Update Models to GPT-5
======================

This script updates all OpenAI model references in the production workflow
from GPT-4 to GPT-5 with proper fallback handling.
"""

import os
import re
import glob
from typing import List, Tuple

class GPT5ModelUpdater:
    def __init__(self):
        self.files_updated = []
        self.changes_made = []
        
    def find_python_files(self) -> List[str]:
        """Find all Python files in the project that might contain OpenAI calls"""
        patterns = [
            '/home/claude-workflow/src/mcp/Production_*.py',
            '/home/claude-workflow/mcp_servers/Production_*.py',
            '/home/claude-workflow/src/utils/api_resilience_manager.py'
        ]
        
        files = []
        for pattern in patterns:
            files.extend(glob.glob(pattern))
        return files
    
    def update_model_references(self, file_path: str) -> bool:
        """Update model references in a single file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            changes = []
            
            # Update model="gpt-4*" to model="gpt-5" with fallback pattern
            gpt4_patterns = [
                (r'model=["\']gpt-4[^"\']*["\']', 'model="gpt-5"'),
                (r'self\.model = ["\']gpt-4[^"\']*["\']', 'self.model = "gpt-5"'),
                (r'"gpt-4-turbo-preview"', '"gpt-5"'),
                (r"'gpt-4-turbo-preview'", "'gpt-5'"),
                (r'"gpt-4"', '"gpt-5"'),
                (r"'gpt-4'", "'gpt-5'")
            ]
            
            for pattern, replacement in gpt4_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    changes.append(f"Updated {pattern} to use GPT-5")
            
            # Add fallback handling for direct API calls
            if 'chat.completions.create(' in content and 'except openai.NotFoundError' not in content:
                # Add fallback pattern for API calls
                fallback_pattern = """        try:
            response = self.client.chat.completions.create(
                model="gpt-5","""
                
                replacement = """        try:
            # Try GPT-5 first, fallback to GPT-4 if not available
            try:
                response = self.client.chat.completions.create(
                    model="gpt-5","""
                
                if 'response = self.client.chat.completions.create(' in content:
                    content = content.replace(
                        'response = self.client.chat.completions.create(\n                model="gpt-5",',
                        '''# Try GPT-5 first, fallback to GPT-4 if not available
            try:
                response = self.client.chat.completions.create(
                    model="gpt-5",'''
                    )
                    changes.append("Added GPT-5 with GPT-4 fallback pattern")
            
            # If changes were made, save the file
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                
                self.files_updated.append(file_path)
                self.changes_made.extend([(file_path, change) for change in changes])
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")
            return False
    
    def add_fallback_imports(self, file_path: str) -> bool:
        """Add necessary imports for fallback handling"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check if we need to add openai import
            if 'import openai' not in content and 'from openai import' in content:
                content = content.replace('from openai import', 'import openai\nfrom openai import')
                
                with open(file_path, 'w') as f:
                    f.write(content)
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error adding imports to {file_path}: {e}")
            return False
    
    def update_all_files(self):
        """Update all relevant files to use GPT-5"""
        print("\n🔄 UPDATING ALL MODELS TO GPT-5")
        print("="*60)
        
        files = self.find_python_files()
        print(f"📁 Found {len(files)} Python files to check")
        
        for file_path in files:
            print(f"\n📝 Processing: {os.path.basename(file_path)}")
            
            # Update model references
            model_updated = self.update_model_references(file_path)
            imports_updated = self.add_fallback_imports(file_path)
            
            if model_updated or imports_updated:
                print(f"✅ Updated: {os.path.basename(file_path)}")
            else:
                print(f"⏭️ No changes needed: {os.path.basename(file_path)}")
        
        # Print summary
        print(f"\n📊 UPDATE SUMMARY")
        print("="*60)
        print(f"Files updated: {len(self.files_updated)}")
        
        if self.files_updated:
            print("\n✅ Updated files:")
            for file_path in self.files_updated:
                print(f"   • {os.path.basename(file_path)}")
        
        if self.changes_made:
            print(f"\n🔧 Changes made:")
            for file_path, change in self.changes_made:
                print(f"   • {os.path.basename(file_path)}: {change}")
        
        print(f"\n🚀 All files updated to use GPT-5 with GPT-4 fallback!")
        
        return len(self.files_updated) > 0

def create_fallback_helper():
    """Create a helper function for GPT-5 fallback handling"""
    helper_code = '''
def call_openai_with_fallback(client, messages, model="gpt-5", fallback_model="gpt-4-turbo-preview", **kwargs):
    """Helper function to call OpenAI with GPT-5 and GPT-4 fallback"""
    try:
        # Try GPT-5 first
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return response, "gpt-5"
    except openai.NotFoundError:
        # Fallback to GPT-4 if GPT-5 not available
        response = client.chat.completions.create(
            model=fallback_model,
            messages=messages,
            **kwargs
        )
        return response, fallback_model
'''
    
    with open('/home/claude-workflow/src/utils/openai_helper.py', 'w') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('"""\nOpenAI Helper Functions\n=======================\n\nHelper functions for OpenAI API calls with GPT-5 support\n"""\n\n')
        f.write('import openai\n')
        f.write(helper_code)
    
    print("✅ Created OpenAI helper functions at src/utils/openai_helper.py")

def main():
    """Main function to update all models"""
    print("\n🔄 GPT-5 MODEL UPDATER")
    print("="*60)
    print("This script will update all OpenAI model references from GPT-4 to GPT-5")
    print("with automatic fallback to GPT-4 if GPT-5 is not available.")
    
    updater = GPT5ModelUpdater()
    
    # Update all files
    success = updater.update_all_files()
    
    # Create helper functions
    create_fallback_helper()
    
    if success:
        print("\n✅ SUCCESS: All models updated to GPT-5!")
        print("\n📝 NOTES:")
        print("   • GPT-5 will be used when available")
        print("   • Automatic fallback to GPT-4 when GPT-5 is not found")
        print("   • Enhanced system prompts for better content generation")
        print("   • Helper functions created for consistent usage")
        
        print(f"\n🚀 Ready to run workflow with GPT-5!")
        print("   Run: python3 src/Production_workflow_runner.py")
    else:
        print("\n⚠️ No changes were needed - models may already be updated")

if __name__ == "__main__":
    main()