#!/bin/bash

# ACTORS Clojure System with Registers and Handlers - Development Startup Script
# This script starts the development environment with register and handler examples

echo "🚀 Starting ACTORS Clojure System with Registers and Handlers..."

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

# Test the register and handler system
echo "🧪 Testing register and handler system..."
clj -M -e "(require 'actors.minimal-registers-handlers) (println \"✅ Register and handler system loaded successfully\")"

if [ $? -eq 0 ]; then
    echo "✅ Register and handler test passed"
else
    echo "❌ Register and handler test failed"
    exit 1
fi

# Start the development environment
echo "🔧 Starting development environment with registers and handlers..."
echo "   - Loading dependencies..."
echo "   - Starting REPL with development tools..."
echo ""

# Start Clojure REPL with development profile
clj -M:dev -e "
(require 'actors.simple-core)
(require 'actors.simple-procedures)
(require 'actors.grid-state)
(require 'actors.kawpow-consciousness)
(require 'actors.minimal-registers-handlers)
(println \"🎉 ACTORS Clojure System with Registers and Handlers Ready!\")
(println \"\")
(println \"Available modules:\")
(println \"  actors.simple-core - Core functional system\")
(println \"  actors.simple-procedures - Comprehensive procedures\")
(println \"  actors.grid-state - Grid state management with lambdas\")
(println \"  actors.kawpow-consciousness - KawPow consciousness signal generation\")
(println \"  actors.minimal-registers-handlers - Register and handler system\")
(println \"\")
(println \"Register and Handler Features:\")
(println \"  Event Creation - Create and emit events with data\")
(println \"  Handler Registration - Register event handlers with functions\")
(println \"  Register Management - Create and update data registers\")
(println \"  Callback Execution - Execute callbacks with error handling\")
(println \"  Event Processing - Process events through handler chains\")
(println \"  Financial Handlers - Market data, trading signals, portfolio updates\")
(println \"  Event-Driven Architecture - Asynchronous event processing\")
(println \"\")
(println \"Available functions:\")
(println \"  (actors.simple-core/demo-functionality) - Core system demo\")
(println \"  (actors.simple-procedures/run-all-procedure-demos) - All procedure demos\")
(println \"  (actors.grid-state/run-all-grid-demos) - All grid demos\")
(println \"  (actors.kawpow-consciousness/run-all-kawpow-demos) - All KawPow demos\")
(println \"  (actors.minimal-registers-handlers/demo-event-creation) - Event creation demo\")
(println \"  (actors.minimal-registers-handlers/demo-register-updates) - Register updates demo\")
(println \"  (actors.minimal-registers-handlers/demo-callback-execution) - Callback execution demo\")
(println \"  (actors.minimal-registers-handlers/demo-integrated-workflow) - Integrated workflow demo\")
(println \"  (actors.minimal-registers-handlers/run-all-minimal-register-handler-demos) - All register/handler demos\")
(println \"\")
(println \"Try: (actors.minimal-registers-handlers/run-all-minimal-register-handler-demos) to see event-driven architecture!\")
(println \"\")
(println \"Press Ctrl+C to stop\")
"
