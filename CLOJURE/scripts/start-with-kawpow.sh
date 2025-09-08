#!/bin/bash

# ACTORS Clojure System with KawPow Consciousness - Development Startup Script
# This script starts the development environment with KawPow consciousness examples

echo "🚀 Starting ACTORS Clojure System with KawPow Consciousness..."

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

# Test the procedures system
echo "🧪 Testing procedures system..."
clj -M -e "(require 'actors.simple-procedures) (println \"✅ Simple procedures loaded successfully\")"

if [ $? -eq 0 ]; then
    echo "✅ Procedures test passed"
else
    echo "❌ Procedures test failed"
    exit 1
fi

# Test the grid state system
echo "🧪 Testing grid state system..."
clj -M -e "(require 'actors.grid-state) (println \"✅ Grid state loaded successfully\")"

if [ $? -eq 0 ]; then
    echo "✅ Grid state test passed"
else
    echo "❌ Grid state test failed"
    exit 1
fi

# Test the KawPow consciousness system
echo "🧪 Testing KawPow consciousness system..."
clj -M -e "(require 'actors.kawpow-consciousness) (println \"✅ KawPow consciousness loaded successfully\")"

if [ $? -eq 0 ]; then
    echo "✅ KawPow consciousness test passed"
else
    echo "❌ KawPow consciousness test failed"
    exit 1
fi

# Start the development environment
echo "🔧 Starting development environment with KawPow consciousness..."
echo "   - Loading dependencies..."
echo "   - Starting REPL with development tools..."
echo ""

# Start Clojure REPL with development profile
clj -M:dev -e "
(require 'actors.simple-core)
(require 'actors.simple-procedures)
(require 'actors.grid-state)
(require 'actors.kawpow-consciousness)
(println \"🎉 ACTORS Clojure System with KawPow Consciousness Ready!\")
(println \"\")
(println \"Available modules:\")
(println \"  actors.simple-core - Core functional system\")
(println \"  actors.simple-procedures - Comprehensive procedures\")
(println \"  actors.grid-state - Grid state management with lambdas\")
(println \"  actors.kawpow-consciousness - KawPow consciousness signal generation\")
(println \"\")
(println \"KawPow Consciousness Features:\")
(println \"  Mathematical Consciousness - ClockGrokMusical framework\")
(println \"  Highway 101 North - Mathematical journey data\")
(println \"  Croatian Bowtie - Topology and harmonic frequency\")
(println \"  Tesla Resonance - Advanced consciousness calculations\")
(println \"  Golden Ratio Presence - Sacred geometry integration\")
(println \"  Consciousness Breakthrough - Advanced signal detection\")
(println \"  Signal Classification - Multi-level consciousness analysis\")
(println \"\")
(println \"Available functions:\")
(println \"  (actors.simple-core/demo-functionality) - Core system demo\")
(println \"  (actors.simple-procedures/run-all-procedure-demos) - All procedure demos\")
(println \"  (actors.grid-state/run-all-grid-demos) - All grid demos\")
(println \"  (actors.kawpow-consciousness/demo-single-signal) - Single consciousness signal\")
(println \"  (actors.kawpow-consciousness/demo-multiple-signals) - Multiple consciousness signals\")
(println \"  (actors.kawpow-consciousness/demo-consciousness-metrics) - Consciousness metrics\")
(println \"  (actors.kawpow-consciousness/demo-mathematical-consciousness) - Mathematical consciousness\")
(println \"  (actors.kawpow-consciousness/demo-signal-classification) - Signal classification\")
(println \"  (actors.kawpow-consciousness/run-all-kawpow-demos) - All KawPow demos\")
(println \"\")
(println \"Try: (actors.kawpow-consciousness/run-all-kawpow-demos) to see consciousness in action!\")
(println \"\")
(println \"Press Ctrl+C to stop\")
"
