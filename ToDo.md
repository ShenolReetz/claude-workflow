# Project TODO List

## URGENT: Video Generation & Star Rating Fix

### 🔥 **HIGH PRIORITY: Fix Video Generation & Review Components**

#### **Current Issues:**
1. **Video Generation Error** - Videos are failing to render (Error: Error rendering video)
2. **Star Rating Implementation** - Need proper v2 review component from documentation
3. **Unicode Stars Don't Work** - Remove all Unicode star approaches completely
4. **Component Implementation** - Use advanced/070 component correctly

#### **Required Tasks:**

##### **1. Fix Video Generation Error** 
- **Status:** ❌ FAILING - All videos showing "Error: Error rendering video"
- **Action:** Debug and fix whatever is causing JSON2Video render failures
- **Test:** Ensure videos complete successfully with "success": true

##### **2. Implement Proper v2 Review Component**
- **Status:** 🔄 NEEDS IMPLEMENTATION
- **Source:** Use advanced/070 component from JSON2Video_Elements.md documentation
- **Format:** Keep ⭐⭐⭐⭐⭐ 4.X/5 (X,XXX reviews) visual format but with proper component
- **Action:** Replace current star rendering with correct advanced/070 implementation

##### **4. Use Advanced/070 Component Correctly**
- **Status:** 🔄 NEEDS PROPER IMPLEMENTATION
- **Reference:** Follow exact format from documentation
- **Components:**
  ```json
  {
    "type": "component",
    "component": "advanced/070",
    "settings": {
      "rating": {
        "value": 4.2,
        "symbol": "star", 
        "size": "8vw",
        "color": "#FFD700",
        "off-color": "rgba(255,255,255,0.2)"
      }
    }
  }
  ```
- **Plus separate text element:** `"4.2/5 (1,234 reviews)"`

##### **5. Preserve Format Requirements**
- **Visual Result:** Stars + "4.X/5 (X,XXX reviews)"
- **Implementation:** Component for stars + text element for rating/reviews
- **Files to Update:** 
  - `mcp_servers/json2video_enhanced_server_v2.py`
  - `mcp_servers/Test_json2video_enhanced_server_v2.py`

---

## Current Session Break - Resume Tasks

### 🎯 **PRIORITY: Text-to-Speech Timing Validation MCP**

#### **Context:**
Video scenes have strict timing requirements:
- **Intro:** 5 seconds max
- **Outro:** 5 seconds max  
- **Products:** 9 seconds max each

All titles and descriptions are converted to audio via Text-to-Speech and must fit within these scene durations.

#### **Required MCP Implementation:**

##### **1. Create Text Length Validation MCP Server**
- **File:** `mcp_servers/text_length_validation_server.py`
- **Purpose:** Validate text length against TTS timing requirements
- **Functionality:**
  - Calculate estimated TTS duration for given text
  - Compare against scene timing limits (5s intro/outro, 9s products)
  - Return validation status: "Approved" or "TooLong"

##### **2. Create Text Length Validation MCP Agent**  
- **File:** `src/mcp/text_length_validation_agent_mcp.py`
- **Purpose:** Orchestrate text validation workflow
- **Functionality:**
  - Fetch content from Airtable
  - Validate all text fields via MCP server
  - Update Airtable status columns with results

##### **3. Airtable Status Column Updates**
The MCP must update these **existing** Airtable columns with `"Approved"` value when validation passes:

**Video Content Columns (5 second limit):**
- **`VideoTitleStatus`** - Based on `VideoTitle` length validation
- **`VideoDescriptionStatus`** - Based on `VideoDescription` length validation

**Product Content Columns (9 second limit each):**
- **`ProductNo1TitleStatus`** - Based on `ProductNo1Title` length validation
- **`ProductNo1DescriptionStatus`** - Based on `ProductNo1Description` length validation
- **`ProductNo2TitleStatus`** - Based on `ProductNo2Title` length validation
- **`ProductNo2DescriptionStatus`** - Based on `ProductNo2Description` length validation
- **`ProductNo3TitleStatus`** - Based on `ProductNo3Title` length validation
- **`ProductNo3DescriptionStatus`** - Based on `ProductNo3Description` length validation
- **`ProductNo4TitleStatus`** - Based on `ProductNo4Title` length validation
- **`ProductNo4DescriptionStatus`** - Based on `ProductNo4Description` length validation
- **`ProductNo5TitleStatus`** - Based on `ProductNo5Title` length validation
- **`ProductNo5DescriptionStatus`** - Based on `ProductNo5Description` length validation

**Status Values:** 
- `"Approved"` - Text fits within timing requirements
- `"Pending"` - Awaiting validation or needs processing
- `"Rejected"` - Text exceeds maximum scene duration (needs shortening)

**EXACT COLUMN NAMES FOR IMPLEMENTATION:**

📊 **Video Content Status Columns (5-second limit):**
```
VideoTitleStatus        → Validates: VideoTitle field
VideoDescriptionStatus  → Validates: VideoDescription field
```

📦 **Product Content Status Columns (9-second limit each):**
```
ProductNo1TitleStatus       → Validates: ProductNo1Title field
ProductNo1DescriptionStatus → Validates: ProductNo1Description field
ProductNo2TitleStatus       → Validates: ProductNo2Title field
ProductNo2DescriptionStatus → Validates: ProductNo2Description field
ProductNo3TitleStatus       → Validates: ProductNo3Title field
ProductNo3DescriptionStatus → Validates: ProductNo3Description field
ProductNo4TitleStatus       → Validates: ProductNo4Title field
ProductNo4DescriptionStatus → Validates: ProductNo4Description field
ProductNo5TitleStatus       → Validates: ProductNo5Title field
ProductNo5DescriptionStatus → Validates: ProductNo5Description field
```

📋 **Total Status Columns to Update:** 12 columns

🔄 **Status Update Workflow:**
1. **Initial State:** All columns start as `"Pending"` or empty
2. **Validation Process:** Each text field is validated against timing requirements
3. **Status Assignment:**
   - `"Approved"` → Text fits within timing requirements
   - `"Rejected"` → Text exceeds timing limits (triggers regeneration)
   - `"Pending"` → Awaiting validation or during regeneration process
4. **Regeneration Cycle:** Failed fields → "Pending" → Regenerate → Re-validate → "Approved"/"Rejected"
5. **Final State:** All columns should be either "Approved" or "Rejected"

#### **4. Technical Implementation Details**

##### **Text-to-Speech Duration Calculation:**
- Use average speaking rate: ~150-180 words per minute
- Calculate: `(word_count / speaking_rate) * 60 = seconds`
- Add buffer for natural speech pauses (10-20%)

##### **Validation Logic:**
```python
def validate_text_timing(text: str, max_seconds: int) -> str:
    """
    Validate if text fits within timing requirements
    Returns: "Approved", "Pending", or "Rejected"
    """
    word_count = len(text.split())
    speaking_rate = 150  # words per minute
    estimated_seconds = (word_count / speaking_rate) * 60 * 1.2  # 20% buffer
    
    return "Approved" if estimated_seconds <= max_seconds else "Rejected"
```

##### **Field Validation Mapping:**
```python
validation_fields = {
    # Video fields (5 second limit)
    'VideoTitle': {'column': 'VideoTitleStatus', 'max_seconds': 5},
    'VideoDescription': {'column': 'VideoDescriptionStatus', 'max_seconds': 5},
    
    # Product fields (9 second limit each)
    'ProductNo1Title': {'column': 'ProductNo1TitleStatus', 'max_seconds': 9},
    'ProductNo1Description': {'column': 'ProductNo1DescriptionStatus', 'max_seconds': 9},
    'ProductNo2Title': {'column': 'ProductNo2TitleStatus', 'max_seconds': 9},
    'ProductNo2Description': {'column': 'ProductNo2DescriptionStatus', 'max_seconds': 9},
    'ProductNo3Title': {'column': 'ProductNo3TitleStatus', 'max_seconds': 9},
    'ProductNo3Description': {'column': 'ProductNo3DescriptionStatus', 'max_seconds': 9},
    'ProductNo4Title': {'column': 'ProductNo4TitleStatus', 'max_seconds': 9},
    'ProductNo4Description': {'column': 'ProductNo4DescriptionStatus', 'max_seconds': 9},
    'ProductNo5Title': {'column': 'ProductNo5TitleStatus', 'max_seconds': 9},
    'ProductNo5Description': {'column': 'ProductNo5DescriptionStatus', 'max_seconds': 9},
}
```

#### **5. Workflow Integration**

##### **Production Workflow Integration:**
- Add step in `src/workflow_runner.py` after content generation
- Integrate before video generation to ensure timing compliance
- Position: After text generation, before audio generation

##### **Test Workflow Integration:**
- Create `mcp_servers/Test_text_length_validation_server.py`
- Create `src/mcp/Test_text_length_validation_agent_mcp.py`
- Add step in `src/Test_workflow_runner.py`
- Test with existing 2-word default audio (should always pass validation)

#### **6. Error Handling & Remediation**

##### **When Text is Rejected:**
- Log specific field that failed validation
- Provide word count and estimated duration
- Suggest text truncation or regeneration
- Option to trigger content regeneration with shorter prompts

##### **Logging Example:**
```
❌ ProductNo3Description rejected: 45 words, ~18.5 seconds (limit: 9 seconds)
✅ VideoTitle approved: 8 words, ~3.2 seconds (limit: 5 seconds)
⏳ ProductNo1Title pending: awaiting validation
```

#### **7. Configuration & Testing**

##### **Configuration Options:**
- Adjustable speaking rate (default: 150 WPM)
- Configurable buffer percentage (default: 20%)
- Enable/disable strict mode (fail workflow vs warn only)

##### **Testing Requirements:**
- Test with various text lengths
- Validate timing calculations accuracy
- Ensure Airtable updates work correctly
- Integration test with full workflow

---

## **Implementation Priority Order:**

### **Phase 1: Core MCP Development**
1. **[✅]** Create `mcp_servers/text_length_validation_server.py`
2. **[✅]** Create `src/mcp/text_length_validation_agent_mcp.py`
3. **[✅]** Implement TTS duration calculation logic
4. **[✅]** Implement Airtable status column updates

### **Phase 2: Test Environment Integration**
1. **[✅]** Create Test versions with `Test_` prefix
2. **[✅]** Integrate into `src/Test_workflow_runner.py`
3. **[ ]** Test with default 2-word audio content
4. **[ ]** Verify all status columns update correctly

### **Phase 3: Production Integration**
1. **[✅]** Integrate into `src/workflow_runner.py`
2. **[✅]** Position after content generation, before audio generation
3. **[ ]** Test with real content generation
4. **[ ]** Verify timing compliance with actual TTS generation

### **Phase 4: Error Handling & Optimization**
1. **[✅]** Implement content regeneration triggers for failed validation
2. **[✅]** Add configuration options for timing adjustments
3. **[✅]** Create comprehensive logging and monitoring
4. **[✅]** Documentation and integration guides

---

## **Future Enhancements (Lower Priority)**

### **Advanced TTS Integration:**
- **[ ]** Direct integration with ElevenLabs API for accurate timing
- **[ ]** Voice-specific timing calibration
- **[ ]** Real-time duration measurement vs estimation

### **Content Optimization:**
- **[ ]** Automatic text shortening for failed validations
- **[ ]** Intelligent summarization for overly long descriptions
- **[ ]** Template-based content regeneration with length constraints

### **Monitoring & Analytics:**
- **[ ]** Track validation success rates
- **[ ]** Analyze common failure patterns
- **[ ]** Generate timing optimization reports

---

## **Technical Notes:**

### **Dependencies:**
- Existing Airtable MCP integration
- Text processing utilities
- Workflow integration framework

### **Performance Considerations:**
- Validation should be fast (< 1 second per record)
- Batch processing for multiple records
- Minimal API calls required

### **Integration Points:**
- Must work with existing content generation
- Compatible with Test workflow optimizations
- Fits into video prerequisite validation system

---

*This TODO list should be implemented after the current break to ensure proper TTS timing compliance in video generation.*