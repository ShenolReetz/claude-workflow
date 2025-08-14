#!/bin/bash
# Redis Setup Script for Production Workflow
# ============================================

echo "🚀 Setting up Redis for Production Workflow..."

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "📦 Installing Redis..."
    sudo apt-get update
    sudo apt-get install -y redis-server redis-tools
else
    echo "✅ Redis is already installed"
fi

# Create Redis configuration for production
echo "📝 Creating optimized Redis configuration..."
cat > /tmp/redis-workflow.conf << 'EOF'
# Redis Configuration for Production Workflow
# Optimized for caching with persistence

# Network
bind 127.0.0.1 ::1
port 6379
protected-mode yes

# Persistence - Save to disk for cache survival across restarts
save 900 1      # Save after 900 sec (15 min) if at least 1 key changed
save 300 10     # Save after 300 sec (5 min) if at least 10 keys changed
save 60 10000   # Save after 60 sec if at least 10000 keys changed
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename workflow-cache.rdb
dir /var/lib/redis

# Memory Management
maxmemory 512mb
maxmemory-policy allkeys-lru  # Remove least recently used keys when memory limit reached

# Logging
loglevel notice
logfile /var/log/redis/workflow-redis.log

# Performance
databases 1  # Only need one database for caching
tcp-keepalive 300
timeout 0

# Lazy freeing (performance optimization)
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes
replica-lazy-flush yes

# Disable dangerous commands in production
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG "CONFIG_workflow_only"
EOF

# Copy configuration to proper location
sudo cp /tmp/redis-workflow.conf /etc/redis/redis-workflow.conf

# Create systemd service for workflow Redis instance
echo "🔧 Creating systemd service..."
sudo cat > /tmp/redis-workflow.service << 'EOF'
[Unit]
Description=Redis Cache for Production Workflow
After=network.target

[Service]
Type=notify
ExecStart=/usr/bin/redis-server /etc/redis/redis-workflow.conf --supervised systemd
ExecStop=/usr/bin/redis-cli -p 6379 shutdown
TimeoutStopSec=30
Restart=always
RestartSec=5
User=redis
Group=redis

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/var/lib/redis /var/log/redis

[Install]
WantedBy=multi-user.target
EOF

sudo cp /tmp/redis-workflow.service /etc/systemd/system/redis-workflow.service

# Reload systemd and start Redis
echo "🚦 Starting Redis service..."
sudo systemctl daemon-reload
sudo systemctl enable redis-workflow
sudo systemctl start redis-workflow

# Wait for Redis to start
sleep 2

# Test Redis connection
echo "🔍 Testing Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running and responding!"
    redis-cli INFO server | grep redis_version
    
    # Set test key
    redis-cli SET test:key "Redis is working!" EX 60
    TEST_VALUE=$(redis-cli GET test:key)
    if [ "$TEST_VALUE" = "Redis is working!" ]; then
        echo "✅ Redis read/write test successful!"
    else
        echo "⚠️ Redis read/write test failed"
    fi
else
    echo "❌ Redis is not responding. Trying to start default Redis service..."
    sudo systemctl start redis-server
    sleep 2
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Default Redis service started successfully!"
    else
        echo "❌ Failed to start Redis. Please check system logs."
        exit 1
    fi
fi

# Create Python test script
cat > /tmp/test_redis_cache.py << 'EOF'
#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('/home/claude-workflow')
from src.utils.cache_manager import get_cache_manager, CacheManager

async def test_redis():
    print("🔍 Testing Redis from Python...")
    cache = await get_cache_manager()
    
    # Test set and get
    await cache.set(CacheManager.CATEGORY_PRODUCTS, "test_key", {"data": "test_value"}, ttl=60)
    result = await cache.get(CacheManager.CATEGORY_PRODUCTS, "test_key")
    
    if result and result.get("data") == "test_value":
        print("✅ Python Redis integration working!")
        stats = await cache.get_stats()
        print(f"📊 Cache stats: {stats}")
        return True
    else:
        print("❌ Python Redis integration failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_redis())
    sys.exit(0 if success else 1)
EOF

# Test Python integration
echo "🐍 Testing Python Redis integration..."
python3 /tmp/test_redis_cache.py

echo ""
echo "========================================="
echo "Redis Setup Complete!"
echo "========================================="
echo "Redis is now running and configured for:"
echo "  • 512MB memory limit"
echo "  • LRU eviction policy"
echo "  • Persistence to disk"
echo "  • Optimized for caching"
echo ""
echo "To monitor Redis:"
echo "  redis-cli INFO stats"
echo "  redis-cli MONITOR"
echo ""
echo "To check cache usage:"
echo "  redis-cli DBSIZE"
echo "  redis-cli INFO memory"
echo "========================================="