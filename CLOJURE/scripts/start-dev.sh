#!/bin/bash

# ACTORS Clojure Functional System - Development Startup Script
# This script starts the development environment with all necessary components

echo "🚀 Starting ACTORS Clojure Functional System Development Environment..."

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

# Start the development environment
echo "🔧 Starting development environment..."
echo "   - Loading dependencies..."
echo "   - Starting REPL with development tools..."
echo "   - Web server will be available at http://localhost:8080"
echo ""

# Start Clojure REPL with development profile
clj -M:dev -e "
(require 'user)
(println \"🎉 ACTORS Clojure Development Environment Ready!\")
(println \"\")
(println \"Available commands:\")
(println \"  (user/start-dev-system) - Start the complete system\")
(println \"  (user/run-all-demos) - Run all demonstration functions\")
(println \"  (user/quick-test) - Quick functionality test\")
(println \"  (user/reload!) - Reload all namespaces\")
(println \"\")
(println \"Try: (user/quick-test) to get started!\")
(println \"\")
(println \"Web API will be available at:\")
(println \"  http://localhost:8080/api/\")
(println \"  http://localhost:8080/health\")
(println \"\")
(println \"Press Ctrl+C to stop the server\")
"
