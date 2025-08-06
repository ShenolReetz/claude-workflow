# TODO List - Production Flow Implementation

## ✅ TODO List Updated for Production Flow Implementation

### 📋 Production Flow Conversion Plan:

1. Copy Test_workflow_runner.py to create Production_workflow_runner.py
2. Rename class from TestContentPipelineOrchestrator to ProductionContentPipelineOrchestrator
3. Replace hardcoded config with real API keys from config/api_keys.json
4. Convert all Test MCP Servers to Production versions with real API calls
5. Convert all Test MCP Agents to Production versions with real API calls
6. Replace Claude API with OpenAI API for content generation (titles, descriptions)
7. Replace hardcoded images with OpenAI DALL-E API for photo generation
8. Replace hardcoded scraping with ScrapingDog API for Amazon product scraping
9. Replace hardcoded audio with ElevenLabs API for voice generation
10. Update all import statements to use production MCP servers and agents
11. Keep Test_workflow_runner.py structure but replace hardcoded values with dynamic API calls
12. Ensure all APIs use the provided keys: OpenAI, ScrapingDog, ElevenLabs, Airtable, etc.
13. Maintain the same workflow steps and expert agent integration
14. Test production workflow integration and API connectivity

### 📊 JSON2Video Schema Improvements (Based on Official Documentation Analysis):

15. **Duration Consistency Fixes:**
    - Add explicit `"duration": 9` to all product scenes (Product 2, 3, 4)
    - Add explicit `"duration": 5` to intro/outro scenes
    - Ensure all scenes have consistent duration properties

16. **Audio Duration Synchronization:**
    - Validate ElevenLabs audio duration matches scene duration exactly
    - Add audio duration validation (audio ≤ scene duration)
    - Implement audio trimming/padding if duration mismatch occurs

17. **Scene Transition Standardization:**
    - Apply consistent `"slideright"` transitions to all product scenes
    - Standardize transition duration to `0.5` seconds
    - Ensure intro uses `"smoothright"` transition

18. **Dynamic Content Integration Validation:**
    - Add text length validation for generated titles within element boundaries
    - Replace Unsplash URLs with dynamic Amazon product images
    - Ensure rating/review/price components match scraped data exactly

19. **ElevenLabs Audio Integration:**
    - Configure subtitle auto-generation from ElevenLabs audio
    - Validate subtitle timing matches audio speech patterns
    - Ensure subtitle styling remains consistent with current schema

20. **Production Quality Controls:**
    - Add schema validation before JSON2Video API calls
    - Implement timing consistency checks across all elements
    - Add fallback handling for audio/image loading failures

### 🎯 Key Requirements:
- Follow exact Test_workflow_runner.py structure (proven and tested)
- Replace hardcoded values with dynamic API generation
- Use OpenAI instead of Claude for content generation
- Use OpenAI DALL-E for image generation
- Use ScrapingDog for Amazon scraping
- Use ElevenLabs for audio generation
- Use real Airtable API
- All API keys are provided in config/api_keys.json
- Ready for fine-tuning after initial implementation

### ⚠️ Schema Issues Identified:
- **Duration Missing**: Product scenes 2, 3, 4 need explicit duration values
- **Audio Sync Risk**: ElevenLabs audio must match scene timing precisely  
- **Transition Inconsistency**: Standardize all scene transitions
- **Dynamic Content Validation**: Ensure generated content fits schema constraints

### ✅ Schema Strengths Confirmed:
- **Subtitle Structure**: Ready for ElevenLabs auto-generation
- **Element Timing**: Proper start/duration/fade configurations
- **Text Elements**: Correct positioning and styling
- **Component Integration**: Rating/counter elements properly structured

---
*Last Updated: August 6, 2025*
*Status: Ready for Production Implementation + Schema Refinements*