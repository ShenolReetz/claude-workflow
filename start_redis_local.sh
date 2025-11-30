Hi #!/bin/bash
# Local Redis Start Script (No sudo required)
# ============================================

echo "🚀 Starting local Redis instance..."

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis is not installed. Please install it first:"
    echo "   sudo apt-get update && sudo apt-get install -y redis-server"
    exit 1
fi

# Check if Redis is already running
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is already running!"
    redis-cli INFO server | grep redis_version
    exit 0
fi

# Create local Redis directory
REDIS_DIR="/home/claude-workflow/.redis"
mkdir -p "$REDIS_DIR"
mkdir -p "$REDIS_DIR/data"
mkdir -p "$REDIS_DIR/logs"

# Create minimal Redis configuration
cat > "$REDIS_DIR/redis.conf" << 'EOF'
# Minimal Redis Configuration for Local Development
port 6379
bind 127.0.0.1
daemonize yes
pidfile /home/claude-workflow/.redis/redis.pid
logfile /home/claude-workflow/.redis/logs/redis.log
dir /home/claude-workflow/.redis/data
dbfilename workflow-cache.rdb

# Memory settings
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000
EOF

# Start Redis with local configuration
echo "📝 Starting Redis with local configuration..."
redis-server "$REDIS_DIR/redis.conf"

# Wait for Redis to start
sleep 2

# Test connection
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis started successfully!"
    echo "📊 Redis info:"
    redis-cli INFO server | grep -E "redis_version|tcp_port|uptime_in_seconds"
    
    # Test read/write
    redis-cli SET test:startup "Redis is working!" EX 60 > /dev/null
    TEST_VALUE=$(redis-cli GET test:startup)
    if [ "$TEST_VALUE" = "Redis is working!" ]; then
        echo "✅ Redis read/write test passed!"
    fi
    
    echo ""
    echo "Redis is running at: localhost:6379"
    echo "PID file: $REDIS_DIR/redis.pid"
    echo "Log file: $REDIS_DIR/logs/redis.log"
    echo "Data dir: $REDIS_DIR/data"
    echo ""
    echo "To stop Redis: redis-cli shutdown"
    echo "To monitor: redis-cli monitor"
else
    echo "❌ Failed to start Redis. Check logs at: $REDIS_DIR/logs/redis.log"
    exit 1
fi