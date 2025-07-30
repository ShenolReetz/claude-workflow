# JSON2Video Error Recovery & Prevention Guide

## Project: ZRKDMhlcMEhAtasZ Error Resolution
**Date:** July 30, 2025  
**Error Type:** Schema Validation - Invalid `vertical-align` Property  
**Status:** ✅ **RESOLVED**

---

## 🚨 Critical Error Analysis

### Original Error
```
Error: Property 'vertical-align' is not allowed in movie/scenes[0]/elements[3]/settings
```

### Root Cause
- **Python Cache Issue**: Cached bytecode in `__pycache__` contained older code with `vertical-align` properties
- **Template Source**: Subtitle elements included invalid `"vertical-align": "bottom"` alongside valid `"offset-y": 900`
- **API Rejection**: JSON2Video API rejected the template due to invalid schema properties

### Affected Elements
All subtitle elements across all scenes contained the invalid property:
```json
{
  "type": "subtitles",
  "settings": {
    "vertical-align": "bottom",  // ❌ INVALID
    "offset-y": 900,             // ✅ CORRECT POSITIONING
    "font-size": 80,
    "style": "classic-progressive",
    "font-family": "Roboto",
    "all-caps": true,
    "outline-width": -1
  }
}
```

---

## ✅ Resolution Implemented

### 1. **Python Cache Cleanup** 
```bash
find /home/claude-workflow -name "__pycache__" -type d -exec rm -rf {} +
find /home/claude-workflow -name "*.pyc" -delete
```

### 2. **Code Verification**
- ✅ Current `json2video_enhanced_server_v2.py` is clean (no vertical-align)
- ✅ Only uses `"offset-y": 900` for subtitle positioning
- ✅ All template generation functions verified

### 3. **Enhanced Template Processor**
Updated `json2video_template_processor.py` with:
- **Validation Function**: `validate_and_clean_template()`
- **Automatic Cleanup**: Removes invalid properties
- **Property Detection**: Identifies all variations of vertical-align
- **Logging**: Reports all fixes applied

### 4. **Comprehensive Validator**
Created `json2video_template_validator.py`:
- **Schema Validation**: Checks all element types
- **Error Detection**: Identifies invalid properties
- **Automatic Fixing**: Removes invalid properties and adds correct ones
- **Backup Creation**: Saves original before applying fixes
- **Detailed Reporting**: Comprehensive validation reports

---

## 🛡️ Prevention Measures

### 1. **Template Validation Pipeline**
```python
# Integrated into template processor
def validate_and_clean_template(template: Dict[str, Any]) -> Dict[str, Any]:
    # Removes all invalid properties
    # Ensures correct positioning with offset-y
    # Logs all fixes applied
```

### 2. **Invalid Property Detection**
**Blocked Properties for Subtitles:**
- `vertical-align` (primary issue)
- `vertical_align` 
- `text-align`
- `align`
- `valign`
- `v-align`

### 3. **Correct Positioning Method**
```json
{
  "type": "subtitles",
  "settings": {
    "offset-y": 900,  // ✅ CORRECT - Use this for bottom positioning
    "font-size": 80,
    "style": "classic-progressive"
  }
}
```

### 4. **Development Safeguards**
- **Cache Clearing**: Automated cache cleanup in development
- **Template Validation**: Mandatory validation before API submission
- **Error Recovery**: Automatic error detection and fixing
- **Backup Strategy**: All templates backed up before modification

---

## 🔧 Tools & Scripts

### 1. **Template Validator** (`json2video_template_validator.py`)
```bash
# Validate and fix template
python json2video_template_validator.py template.json

# Validate only (no fixes)
python json2video_template_validator.py template.json --no-fix

# Validate without saving fixed version
python json2video_template_validator.py template.json --no-save
```

### 2. **Template Processor** (`json2video_template_processor.py`)
- Integrated validation during template processing
- Automatic cleanup of invalid properties
- Comprehensive logging of all fixes

### 3. **Error Recovery System** (`error_recovery_system.py`)
- Detects vertical-align errors in API responses
- Automatically applies fixes to templates
- Updates Airtable records with error details

---

## 📋 Recovery Workflow

### When JSON2Video API Errors Occur:

#### 1. **Immediate Response**
```bash
# Clear Python caches
find /home/claude-workflow -name "__pycache__" -type d -exec rm -rf {} +

# Validate current templates
python json2video_template_validator.py [template_file]
```

#### 2. **Error Analysis**
- Check API response for specific error messages
- Identify affected elements and properties
- Determine root cause (cache, template, or code issue)

#### 3. **Template Fixing**
```python
# Use template processor with validation
from json2video_template_processor import process_template, validate_and_clean_template

# Process and validate template
clean_template = validate_and_clean_template(template)
```

#### 4. **Verification**
- Run template validator on fixed template
- Test with JSON2Video API (if credits available)
- Update documentation with findings

#### 5. **Prevention Update**
- Add new invalid properties to validator
- Update error recovery patterns
- Document lessons learned

---

## 🧪 Testing & Validation

### 1. **Template Structure Validation**
```python
# Required elements check
REQUIRED_PROPERTIES = {
    'subtitles': ['type', 'language'],
    'text': ['type', 'text'],
    'image': ['type', 'src'],
    'audio': ['type', 'src'],
    'component': ['type', 'component']
}
```

### 2. **Property Validation**
```python
# Invalid properties detection
INVALID_SUBTITLE_PROPERTIES = [
    'vertical-align',  # Primary issue
    'vertical_align', 
    'text-align',
    'align',
    'valign',
    'v-align'
]
```

### 3. **Positioning Validation**
- Ensure only valid positioning methods are used
- Prefer `offset-y` over alignment properties for subtitles
- Detect conflicting positioning methods

---

## 📊 Success Metrics

### Resolution Success Indicators:
- ✅ **Python Cache Cleared**: No cached bytecode with invalid properties
- ✅ **Template Validator Created**: Comprehensive validation system
- ✅ **Template Processor Enhanced**: Automatic cleanup integration
- ✅ **Error Recovery System**: Handles vertical-align errors automatically
- ✅ **Documentation Complete**: Full recovery workflow documented

### Future Video Generation:
- ✅ **Schema Compliance**: All templates pass JSON2Video validation
- ✅ **Property Validation**: Invalid properties automatically removed
- ✅ **Positioning Correctness**: Only `offset-y` used for subtitle positioning
- ✅ **Error Prevention**: Comprehensive validation prevents API errors

---

## 🔄 Continuous Improvement

### 1. **Error Pattern Learning**
- Document new JSON2Video API restrictions
- Update validator with new invalid properties
- Enhance error recovery patterns

### 2. **Template Evolution**
- Keep templates aligned with JSON2Video API changes
- Regularly validate against latest API specifications
- Maintain backward compatibility where possible

### 3. **Development Best Practices**
- Always validate templates before API submission
- Clear Python caches during development
- Use version control for template changes
- Test with minimal API credit consumption

---

## 📞 Emergency Recovery

### If JSON2Video Projects Fail:

1. **Immediate Action**
   ```bash
   # Clear all caches
   find /home/claude-workflow -name "__pycache__" -exec rm -rf {} +
   
   # Validate template
   python json2video_template_validator.py [template] --fix
   ```

2. **Check Current Code**
   ```bash
   # Verify no vertical-align in current code
   grep -r "vertical-align" mcp_servers/json2video_enhanced_server_v2.py
   # Should return no results
   ```

3. **Re-run Video Generation**
   - Use clean template with fixes applied
   - Monitor for new error patterns
   - Document any new issues found

---

**Last Updated:** July 30, 2025  
**Next Review:** When next JSON2Video API error occurs  
**Responsible:** Error Recovery Specialist Agent