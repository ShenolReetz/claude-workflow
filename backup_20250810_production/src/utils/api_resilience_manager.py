#!/usr/bin/env python3
"""
API Resilience Manager - Handle quotas, rate limits, and fallbacks
===================================================================

Enhanced error recovery system with:
- Circuit breakers for API health
- Exponential backoff with jitter
- Quota tracking and prediction
- Fallback strategies
- Dead letter queue for failed items
- Checkpoint recovery
"""

import asyncio
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable, Any, List
import openai
from openai import RateLimitError, APIError
import logging
import random
from dataclasses import dataclass, asdict
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreaker:
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    success_count: int = 0
    
    # Configuration
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout: int = 60  # seconds
    
    def record_success(self):
        """Record a successful API call"""
        self.success_count += 1
        if self.state == CircuitState.HALF_OPEN and self.success_count >= self.success_threshold:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
    
    def record_failure(self):
        """Record a failed API call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.success_count = 0
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def can_attempt(self) -> bool:
        """Check if we can attempt an API call"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if self.last_failure_time:
                time_since_failure = (datetime.now() - self.last_failure_time).seconds
                if time_since_failure >= self.timeout:
                    self.state = CircuitState.HALF_OPEN
                    return True
            return False
        
        # HALF_OPEN state
        return True

@dataclass
class WorkflowCheckpoint:
    """Checkpoint for workflow recovery"""
    workflow_id: str
    step_name: str
    step_data: Dict
    timestamp: datetime
    status: str = "in_progress"

class APIResilienceManager:
    def __init__(self, config: Dict):
        self.config = config
        self.retry_delays = [1, 2, 5, 10, 30]  # Progressive delays
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.dead_letter_queue: List[Dict] = []
        self.checkpoints: Dict[str, WorkflowCheckpoint] = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Paths for persistence
        self.checkpoint_file = '/home/claude-workflow/workflow_checkpoints.json'
        self.dlq_file = '/home/claude-workflow/dead_letter_queue.json'
        
        # Load existing checkpoints and DLQ
        self._load_persistence()
        
        # API quota tracking
        self.api_usage = {
            'openai': {'calls': 0, 'tokens': 0, 'last_reset': datetime.now()},
            'elevenlabs': {'calls': 0, 'characters': 0, 'last_reset': datetime.now()},
            'scrapingdog': {'calls': 0, 'last_reset': datetime.now()},
            'json2video': {'calls': 0, 'last_reset': datetime.now()}
        }
        # GPT-5 model costs (per 1M tokens)
        self.model_costs = {
            'gpt-5': {'input': 1.25, 'output': 10.00},
            'gpt-5-mini': {'input': 0.25, 'output': 2.00},
            'gpt-5-nano': {'input': 0.05, 'output': 0.40},
            'gpt-4o': {'input': 2.50, 'output': 10.00},
            'gpt-4-turbo': {'input': 10.00, 'output': 30.00}
        }
    
    def _load_persistence(self):
        """Load checkpoints and DLQ from disk"""
        # Load checkpoints
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        value['timestamp'] = datetime.fromisoformat(value['timestamp'])
                        self.checkpoints[key] = WorkflowCheckpoint(**value)
            except Exception as e:
                self.logger.warning(f"Failed to load checkpoints: {e}")
        
        # Load DLQ
        if os.path.exists(self.dlq_file):
            try:
                with open(self.dlq_file, 'r') as f:
                    self.dead_letter_queue = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load DLQ: {e}")
    
    def save_checkpoint(self, workflow_id: str, step_name: str, step_data: Dict):
        """Save workflow checkpoint for recovery"""
        checkpoint = WorkflowCheckpoint(
            workflow_id=workflow_id,
            step_name=step_name,
            step_data=step_data,
            timestamp=datetime.now()
        )
        
        self.checkpoints[f"{workflow_id}_{step_name}"] = checkpoint
        
        # Persist to disk
        try:
            data = {}
            for key, cp in self.checkpoints.items():
                cp_dict = asdict(cp)
                cp_dict['timestamp'] = cp.timestamp.isoformat()
                data[key] = cp_dict
            
            with open(self.checkpoint_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {e}")
    
    def add_to_dlq(self, item: Dict):
        """Add failed item to dead letter queue"""
        item['failed_at'] = datetime.now().isoformat()
        self.dead_letter_queue.append(item)
        
        # Persist to disk
        try:
            with open(self.dlq_file, 'w') as f:
                json.dump(self.dead_letter_queue, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save DLQ: {e}")

    async def call_openai_with_resilience(
        self, 
        client: openai.OpenAI,
        model: str,
        messages: list,
        max_tokens: int = 1000,
        fallback_model: str = "gpt-3.5-turbo"
    ) -> Optional[str]:
        """Call OpenAI with quota handling and fallbacks"""
        
        # Get circuit breaker
        breaker = self._get_circuit_breaker('openai')
        
        # Check if circuit is open
        if not breaker.can_attempt():
            self.logger.warning("OpenAI circuit breaker is OPEN, using fallback")
            return await self._use_openai_fallback(messages[0]['content'])
            
        for attempt, delay in enumerate(self.retry_delays):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens
                )
                
                # Record success in circuit breaker
                breaker.record_success()
                
                # Track API usage
                self.api_usage['openai']['calls'] += 1
                self.api_usage['openai']['tokens'] += max_tokens
                
                return response.choices[0].message.content
                
            except RateLimitError as e:
                self.logger.warning(f"OpenAI rate limit hit (attempt {attempt + 1}): {e}")
                
                if "insufficient_quota" in str(e):
                    # Quota exhausted - use fallback immediately
                    self.logger.error("OpenAI quota exhausted, using fallback")
                    breaker.record_failure()
                    return await self._use_openai_fallback(messages[0]['content'])
                
                # Rate limit - wait and retry
                await asyncio.sleep(delay)
                
            except APIError as e:
                self.logger.warning(f"OpenAI API error (attempt {attempt + 1}): {e}")
                
                if attempt < len(self.retry_delays) - 1:
                    await asyncio.sleep(delay)
                else:
                    # Final attempt failed - try fallback model
                    try:
                        response = client.chat.completions.create(
                            model=fallback_model,
                            messages=messages,
                            max_tokens=max_tokens // 2  # Reduce token usage
                        )
                        return response.choices[0].message.content
                    except:
                        return await self._use_openai_fallback(messages[0]['content'])
                        
            except Exception as e:
                self.logger.error(f"Unexpected OpenAI error: {e}")
                if attempt == len(self.retry_delays) - 1:
                    return await self._use_openai_fallback(messages[0]['content'])
                await asyncio.sleep(delay)
        
        # All attempts failed
        return await self._use_openai_fallback(messages[0]['content'])

    async def call_api_with_backoff(
        self,
        api_func: Callable,
        api_name: str,
        *args,
        **kwargs
    ) -> Any:
        """Generic API call with exponential backoff"""
        
        if self._is_circuit_open(api_name):
            raise Exception(f"{api_name} circuit breaker is open")
            
        for attempt, delay in enumerate(self.retry_delays):
            try:
                result = await api_func(*args, **kwargs)
                self._reset_circuit_breaker(api_name)
                return result
                
            except Exception as e:
                self.logger.warning(f"{api_name} error (attempt {attempt + 1}): {e}")
                
                if "429" in str(e) or "rate limit" in str(e).lower():
                    await asyncio.sleep(delay * 2)  # Longer delay for rate limits
                elif attempt < len(self.retry_delays) - 1:
                    await asyncio.sleep(delay)
                else:
                    self._trip_circuit_breaker(api_name)
                    raise
        
        raise Exception(f"All retry attempts failed for {api_name}")

    async def _use_openai_fallback(self, prompt: str) -> str:
        """Fallback content generation using templates"""
        self.logger.info("Using OpenAI fallback content generation")
        
        # Simple template-based fallback
        if "title" in prompt.lower():
            return "Amazing Product Review - Top Picks 2025"
        elif "description" in prompt.lower():
            return "Check out these incredible product recommendations! Perfect for your needs."
        elif "script" in prompt.lower():
            return "Welcome to this product review! Let's explore some amazing options available on Amazon."
        elif "keywords" in prompt.lower():
            return '["product review", "amazon picks", "best products", "top rated", "2025 review"]'
        else:
            return "Quality content generated with fallback system due to API limitations."

    def _get_circuit_breaker(self, api_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for API"""
        if api_name not in self.circuit_breakers:
            self.circuit_breakers[api_name] = CircuitBreaker()
        return self.circuit_breakers[api_name]
    
    def get_api_health_status(self) -> Dict:
        """Get current status of all APIs"""
        status = {}
        for api_name, breaker in self.circuit_breakers.items():
            status[api_name] = {
                'state': breaker.state.value,
                'failure_count': breaker.failure_count,
                'success_count': breaker.success_count,
                'can_attempt': breaker.can_attempt()
            }
        
        # Add usage metrics
        for api_name, usage in self.api_usage.items():
            if api_name not in status:
                status[api_name] = {}
            status[api_name]['usage'] = usage
            
        return status
    
    def get_checkpoints(self) -> Dict[str, WorkflowCheckpoint]:
        """Get all workflow checkpoints"""
        return self.checkpoints
    
    def get_dlq_items(self) -> List[Dict]:
        """Get items from dead letter queue"""
        return self.dead_letter_queue
    
    def retry_dlq_item(self, index: int) -> Optional[Dict]:
        """Retry an item from the DLQ"""
        if 0 <= index < len(self.dead_letter_queue):
            item = self.dead_letter_queue.pop(index)
            # Save updated DLQ
            try:
                with open(self.dlq_file, 'w') as f:
                    json.dump(self.dead_letter_queue, f, indent=2)
            except Exception as e:
                self.logger.error(f"Failed to update DLQ: {e}")
            return item
        return None