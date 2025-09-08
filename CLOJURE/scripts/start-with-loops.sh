#!/bin/bash

# ACTORS Clojure System with While Loops - Development Startup Script
# This script starts the development environment with while loop examples

echo "🚀 Starting ACTORS Clojure System with While Loops..."

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

# Test the loops system
echo "🧪 Testing while loops system..."
clj -M -e "(require 'actors.loops) (println \"✅ While loops loaded successfully\")"

if [ $? -eq 0 ]; then
    echo "✅ While loops test passed"
else
    echo "❌ While loops test failed"
    exit 1
fi

# Test the loop examples
echo "🧪 Testing loop examples..."
clj -M -e "(require 'actors.loop-examples) (println \"✅ Loop examples loaded successfully\")"

if [ $? -eq 0 ]; then
    echo "✅ Loop examples test passed"
else
    echo "❌ Loop examples test failed"
    exit 1
fi

# Start the development environment
echo "🔧 Starting development environment with while loops..."
echo "   - Loading dependencies..."
echo "   - Starting REPL with development tools..."
echo ""

# Start Clojure REPL with development profile
clj -M:dev -e "
(require 'actors.simple-core)
(require 'actors.loops)
(require 'actors.loop-examples)
(println \"🎉 ACTORS Clojure System with While Loops Ready!\")
(println \"\")
(println \"Available modules:\")
(println \"  actors.simple-core - Core functional system\")
(println \"  actors.loops - Basic while loop patterns\")
(println \"  actors.loop-examples - Comprehensive loop examples\")
(println \"\")
(println \"Available functions:\")
(println \"  (actors.simple-core/demo-functionality) - Core system demo\")
(println \"  (actors.loops/demo-while-loops) - Basic while loops demo\")
(println \"  (actors.loop-examples/demo-basic-while-loops) - Basic loops demo\")
(println \"  (actors.loop-examples/demo-financial-while-loops) - Financial loops demo\")
(println \"  (actors.loop-examples/demo-infinite-while-loops) - Infinite loops demo\")
(println \"  (actors.loop-examples/run-all-loop-demos) - All loop demos\")
(println \"\")
(println \"Try: (actors.loop-examples/run-all-loop-demos) to see all while loops!\")
(println \"\")
(println \"Press Ctrl+C to stop\")
"
