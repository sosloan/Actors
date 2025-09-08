#!/bin/bash

# ACTORS Clojure System with Complete System Inventory - Development Startup Script
# This script starts the development environment with complete system inventory

echo "🚀 Starting ACTORS Clojure System with Complete System Inventory..."

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

# Test all systems
echo "🧪 Testing all systems..."

# Test the simple system
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

# Test the higher order functions system
echo "🧪 Testing higher order functions system..."
clj -M -e "(require 'actors.simple-higher-order-functions) (println \"✅ Higher order functions loaded successfully\")"

if [ $? -eq 0 ]; then
    echo "✅ Higher order functions test passed"
else
    echo "❌ Higher order functions test failed"
    exit 1
fi

# Test the advanced functional patterns system
echo "🧪 Testing advanced functional patterns system..."
clj -M -e "(require 'actors.advanced-functional-patterns) (println \"✅ Advanced functional patterns loaded successfully\")"

if [ $? -eq 0 ]; then
    echo "✅ Advanced functional patterns test passed"
else
    echo "❌ Advanced functional patterns test failed"
    exit 1
fi

# Test the working memoization system
echo "🧪 Testing working memoization system..."
clj -M -e "(require 'actors.working-memoization) (println \"✅ Working memoization loaded successfully\")"

if [ $? -eq 0 ]; then
    echo "✅ Working memoization test passed"
else
    echo "❌ Working memoization test failed"
    exit 1
fi

# Test the system inventory
echo "🧪 Testing system inventory..."
clj -M -e "(require 'actors.system-inventory) (println \"✅ System inventory loaded successfully\")"

if [ $? -eq 0 ]; then
    echo "✅ System inventory test passed"
else
    echo "❌ System inventory test failed"
    exit 1
fi

# Start the development environment
echo "🔧 Starting development environment with complete system inventory..."
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
(require 'actors.simple-higher-order-functions)
(require 'actors.advanced-functional-patterns)
(require 'actors.working-memoization)
(require 'actors.system-inventory)
(println \"🎉 ACTORS Clojure System with Complete System Inventory Ready!\")
(println \"\")
(println \"Available modules:\")
(println \"  actors.simple-core - Core functional system\")
(println \"  actors.simple-procedures - Comprehensive procedures\")
(println \"  actors.grid-state - Grid state management with lambdas\")
(println \"  actors.kawpow-consciousness - KawPow consciousness signal generation\")
(println \"  actors.minimal-registers-handlers - Register and handler system\")
(println \"  actors.simple-higher-order-functions - Higher order functions system\")
(println \"  actors.advanced-functional-patterns - Advanced functional patterns\")
(println \"  actors.working-memoization - Working memoization and data-driven programming\")
(println \"  actors.system-inventory - Complete system inventory\")
(println \"\")
(println \"System Inventory Features:\")
(println \"  Symbol Collection - Collect all symbols from namespaces\")
(println \"  Component Registry - Register and manage system components\")
(println \"  Route Definition - Define API routes for system access\")
(println \"  Action Definition - Define system actions and operations\")
(println \"  State Management - Define and track system states\")
(println \"  Complete Inventory - Comprehensive system overview\")
(println \"\")
(println \"Available functions:\")
(println \"  (actors.simple-core/demo-functionality) - Core system demo\")
(println \"  (actors.simple-procedures/run-all-procedure-demos) - All procedure demos\")
(println \"  (actors.grid-state/run-all-grid-demos) - All grid demos\")
(println \"  (actors.kawpow-consciousness/run-all-kawpow-demos) - All KawPow demos\")
(println \"  (actors.minimal-registers-handlers/run-all-minimal-register-handler-demos) - All register/handler demos\")
(println \"  (actors.simple-higher-order-functions/run-all-simple-higher-order-function-demos) - All higher order function demos\")
(println \"  (actors.advanced-functional-patterns/run-all-advanced-functional-pattern-demos) - All advanced pattern demos\")
(println \"  (actors.working-memoization/run-all-working-demos) - All working memoization demos\")
(println \"  (actors.system-inventory/display-complete-inventory) - Display complete system inventory\")
(println \"\")
(println \"Try: (actors.system-inventory/display-complete-inventory) to see the complete system inventory!\")
(println \"\")
(println \"Press Ctrl+C to stop\")
"
