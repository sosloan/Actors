#!/bin/bash

# ACTORS Clojure System with Grid State - Development Startup Script
# This script starts the development environment with grid state examples

echo "🚀 Starting ACTORS Clojure System with Grid State..."

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

# Start the development environment
echo "🔧 Starting development environment with grid state..."
echo "   - Loading dependencies..."
echo "   - Starting REPL with development tools..."
echo ""

# Start Clojure REPL with development profile
clj -M:dev -e "
(require 'actors.simple-core)
(require 'actors.simple-procedures)
(require 'actors.grid-state)
(println \"🎉 ACTORS Clojure System with Grid State Ready!\")
(println \"\")
(println \"Available modules:\")
(println \"  actors.simple-core - Core functional system\")
(println \"  actors.simple-procedures - Comprehensive procedures\")
(println \"  actors.grid-state - Grid state management with lambdas\")
(println \"\")
(println \"Grid State Features:\")
(println \"  Grid Creation - Create grids with dimensions and initial values\")
(println \"  Lambda Operations - Map, filter, reduce with lambda functions\")
(println \"  Recursive Operations - Recursive fill, search, and path finding\")
(println \"  In-Place Copying - Copy data in place with mutable operations\")
(println \"  Financial Grids - Specialized grids for financial data\")
(println \"  Grid Analysis - Pattern analysis and statistics\")
(println \"\")
(println \"Available functions:\")
(println \"  (actors.simple-core/demo-functionality) - Core system demo\")
(println \"  (actors.simple-procedures/run-all-procedure-demos) - All procedure demos\")
(println \"  (actors.grid-state/demo-basic-grid-operations) - Basic grid operations\")
(println \"  (actors.grid-state/demo-financial-grid) - Financial grid operations\")
(println \"  (actors.grid-state/demo-recursive-operations) - Recursive operations\")
(println \"  (actors.grid-state/demo-lambda-operations) - Lambda operations\")
(println \"  (actors.grid-state/demo-grid-copying) - Grid copying operations\")
(println \"  (actors.grid-state/run-all-grid-demos) - All grid demos\")
(println \"\")
(println \"Try: (actors.grid-state/run-all-grid-demos) to see all grid operations!\")
(println \"\")
(println \"Press Ctrl+C to stop\")
"
