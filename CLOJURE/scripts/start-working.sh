#!/bin/bash

# ACTORS Clojure Working System - Development Startup Script
# This script starts the working development environment

echo "🚀 Starting ACTORS Clojure Working System Development Environment..."

# Check if Clojure is installed
if ! command -v clj &> /dev/null; then
    echo "❌ Clojure CLI not found. Please install Clojure CLI tools."
    echo "   Visit: https://clojure.org/guides/getting_started"
    exit 1
fi

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "❌ Java not found. Please install Java 11 or later."
    exit 1
fi

echo "✅ Clojure and Java found"

# Navigate to the Clojure directory
cd "$(dirname "$0")/.."

echo "📁 Working directory: $(pwd)"

# Check if deps.edn exists
if [ ! -f "deps.edn" ]; then
    echo "❌ deps.edn not found. Please ensure you're in the correct directory."
    exit 1
fi

echo "✅ Project structure verified"

# Test the simple system first
echo "🧪 Testing simple system..."
clj -M -e "(require 'actors.simple-core) (println \"✅ Simple core loaded successfully\")"

if [ $? -eq 0 ]; then
    echo "✅ Simple system test passed"
else
    echo "❌ Simple system test failed"
    exit 1
fi

# Start the development environment
echo "🔧 Starting development environment..."
echo "   - Loading dependencies..."
echo "   - Starting REPL with development tools..."
echo ""

# Start Clojure REPL with development profile
clj -M:dev -e "
(require 'actors.simple-core)
(println \"🎉 ACTORS Clojure Working System Ready!\")
(println \"\")
(println \"Available functions:\")
(println \"  (actors.simple-core/demo-functionality) - Run demonstration\")
(println \"  (actors.simple-core/initialize-system) - Initialize system\")
(println \"  (actors.simple-core/create-market-data \\\"AAPL\\\" 150.25 1000000 0.18)\")
(println \"  (actors.simple-core/create-trading-signal :buy 0.85 {:strategy \\\"ma\\\"})\")
(println \"\")
(println \"Try: (actors.simple-core/demo-functionality) to get started!\")
(println \"\")
(println \"Press Ctrl+C to stop\")
"
