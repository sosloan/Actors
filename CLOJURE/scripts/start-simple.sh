#!/bin/bash

# ACTORS Clojure Simple System - Development Startup Script
# This script starts the simplified development environment

echo "🚀 Starting ACTORS Clojure Simple System Development Environment..."

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
(require 'simple-user)
(println \"🎉 ACTORS Clojure Simple System Ready!\")
(println \"\")
(println \"Available commands:\")
(println \"  (start-simple-system) - Start the complete system\")
(println \"  (run-simple-demo) - Run demonstration functions\")
(println \"  (test-basic-functionality) - Test core functions\")
(println \"  (test-channels) - Test async channels\")
(println \"  (run-all-tests) - Run all tests\")
(println \"\")
(println \"Try: (test-basic-functionality) to get started!\")
(println \"\")
(println \"Press Ctrl+C to stop\")
"
