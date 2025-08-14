#!/usr/bin/env python3
"""
Circuit Breaker Pattern for External API Calls
================================================

Prevents cascade failures by failing fast when external services are down.
Automatically recovers when services become available again.

STATES:
1. CLOSED: Normal operation, requests pass through
2. OPEN: Service is down, requests fail immediately 
3. HALF_OPEN: Testing if service recovered

FEATURES:
- Configurable failure threshold
- Automatic recovery with exponential backoff
- Per-service circuit breakers
- Detailed failure tracking
"""

import asyncio
import time
import logging
from enum import Enum
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import functools

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open" # Testing recovery

@dataclass
class CircuitStats:
    """Statistics for circuit breaker"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    consecutive_failures: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    times_opened: int = 0
    
    @property
    def failure_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.failed_calls / self.total_calls

class CircuitBreaker:
    """Circuit breaker for a single service"""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_requests: int = 3,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker
        
        Args:
            name: Service name for logging
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
            half_open_requests: Test requests in half-open state
            expected_exception: Exception type to catch
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests
        self.expected_exception = expected_exception
        
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        self.half_open_counter = 0
        self.state_changed_at = time.time()
        
        self.logger = logging.getLogger(f"CircuitBreaker.{name}")
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker
        
        Args:
            func: Async function to call
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitOpenError: If circuit is open
            Original exception: If function fails
        """
        async with self._lock:
            # Check if we should attempt the call
            if not self._can_attempt():
                self.logger.warning(f"Circuit OPEN for {self.name} - failing fast")
                raise CircuitOpenError(f"Circuit breaker is OPEN for {self.name}")
            
            # Track if we're testing recovery
            is_testing = self.state == CircuitState.HALF_OPEN
        
        # Attempt the call (outside lock to avoid blocking)
        try:
            start_time = time.time()
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            # Record success
            async with self._lock:
                await self._record_success(elapsed)
            
            return result
            
        except self.expected_exception as e:
            # Record failure
            async with self._lock:
                await self._record_failure(str(e))
            
            # Re-raise the original exception
            raise
    
    def _can_attempt(self) -> bool:
        """Check if we can attempt a request"""
        current_time = time.time()
        
        if self.state == CircuitState.CLOSED:
            return True
        
        elif self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if current_time - self.state_changed_at >= self.recovery_timeout:
                self._transition_to_half_open()
                return True
            return False
        
        elif self.state == CircuitState.HALF_OPEN:
            # Allow limited requests for testing
            return self.half_open_counter < self.half_open_requests
    
    async def _record_success(self, elapsed_time: float):
        """Record successful call"""
        self.stats.total_calls += 1
        self.stats.successful_calls += 1
        self.stats.consecutive_failures = 0
        self.stats.last_success_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_counter += 1
            
            # If enough successful calls, close the circuit
            if self.half_open_counter >= self.half_open_requests:
                self._transition_to_closed()
                self.logger.info(f"Circuit RECOVERED for {self.name} (response time: {elapsed_time:.2f}s)")
    
    async def _record_failure(self, error_msg: str):
        """Record failed call"""
        self.stats.total_calls += 1
        self.stats.failed_calls += 1
        self.stats.consecutive_failures += 1
        self.stats.last_failure_time = time.time()
        
        self.logger.debug(f"Failure #{self.stats.consecutive_failures} for {self.name}: {error_msg[:100]}")
        
        if self.state == CircuitState.HALF_OPEN:
            # Single failure in half-open state opens the circuit again
            self._transition_to_open()
            self.logger.warning(f"Circuit RE-OPENED for {self.name} after recovery test failed")
        
        elif self.state == CircuitState.CLOSED:
            # Check if we've hit the failure threshold
            if self.stats.consecutive_failures >= self.failure_threshold:
                self._transition_to_open()
                self.logger.error(
                    f"Circuit OPENED for {self.name} after {self.stats.consecutive_failures} failures"
                )
    
    def _transition_to_open(self):
        """Transition to OPEN state"""
        self.state = CircuitState.OPEN
        self.state_changed_at = time.time()
        self.stats.times_opened += 1
        self.half_open_counter = 0
    
    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state"""
        self.state = CircuitState.HALF_OPEN
        self.state_changed_at = time.time()
        self.half_open_counter = 0
        self.logger.info(f"Circuit HALF-OPEN for {self.name} - testing recovery")
    
    def _transition_to_closed(self):
        """Transition to CLOSED state"""
        self.state = CircuitState.CLOSED
        self.state_changed_at = time.time()
        self.stats.consecutive_failures = 0
        self.half_open_counter = 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            'name': self.name,
            'state': self.state.value,
            'stats': {
                'total_calls': self.stats.total_calls,
                'successful_calls': self.stats.successful_calls,
                'failed_calls': self.stats.failed_calls,
                'failure_rate': f"{self.stats.failure_rate:.1%}",
                'consecutive_failures': self.stats.consecutive_failures,
                'times_opened': self.stats.times_opened
            },
            'config': {
                'failure_threshold': self.failure_threshold,
                'recovery_timeout': self.recovery_timeout
            }
        }
    
    def reset(self):
        """Reset circuit breaker to initial state"""
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        self.half_open_counter = 0
        self.state_changed_at = time.time()
        self.logger.info(f"Circuit breaker reset for {self.name}")

class CircuitOpenError(Exception):
    """Exception raised when circuit is open"""
    pass

class CircuitBreakerManager:
    """Manages circuit breakers for multiple services"""
    
    # Default configurations per service
    SERVICE_CONFIGS = {
        'openai': {
            'failure_threshold': 3,
            'recovery_timeout': 30,
            'half_open_requests': 2
        },
        'airtable': {
            'failure_threshold': 5,
            'recovery_timeout': 60,
            'half_open_requests': 3
        },
        'scrapingdog': {
            'failure_threshold': 5,
            'recovery_timeout': 120,
            'half_open_requests': 2
        },
        'elevenlabs': {
            'failure_threshold': 3,
            'recovery_timeout': 60,
            'half_open_requests': 2
        },
        'json2video': {
            'failure_threshold': 3,
            'recovery_timeout': 180,
            'half_open_requests': 1
        },
        'google_drive': {
            'failure_threshold': 5,
            'recovery_timeout': 60,
            'half_open_requests': 3
        },
        'youtube': {
            'failure_threshold': 3,
            'recovery_timeout': 120,
            'half_open_requests': 2
        }
    }
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.logger = logging.getLogger("CircuitBreakerManager")
    
    def get_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.breakers:
            config = self.SERVICE_CONFIGS.get(service_name, {
                'failure_threshold': 5,
                'recovery_timeout': 60,
                'half_open_requests': 3
            })
            
            self.breakers[service_name] = CircuitBreaker(
                name=service_name,
                **config
            )
            
            self.logger.info(f"Created circuit breaker for {service_name}")
        
        return self.breakers[service_name]
    
    async def call(self, service_name: str, func: Callable, *args, **kwargs) -> Any:
        """Execute function through appropriate circuit breaker"""
        breaker = self.get_breaker(service_name)
        return await breaker.call(func, *args, **kwargs)
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers"""
        return {
            name: breaker.get_status()
            for name, breaker in self.breakers.items()
        }
    
    def reset_all(self):
        """Reset all circuit breakers"""
        for breaker in self.breakers.values():
            breaker.reset()
        self.logger.info("All circuit breakers reset")

# Singleton instance
_manager_instance: Optional[CircuitBreakerManager] = None

def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """Get singleton circuit breaker manager"""
    global _manager_instance
    
    if _manager_instance is None:
        _manager_instance = CircuitBreakerManager()
    
    return _manager_instance

# Decorator for protecting functions with circuit breaker
def circuit_breaker(service_name: str):
    """
    Decorator to protect async functions with circuit breaker
    
    Usage:
        @circuit_breaker('openai')
        async def call_openai_api():
            # API call
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            manager = get_circuit_breaker_manager()
            return await manager.call(service_name, func, *args, **kwargs)
        return wrapper
    return decorator