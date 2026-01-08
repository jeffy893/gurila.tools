#!/bin/bash

# PySpark Installation Script for macOS
# ====================================

echo "🍺 Installing PySpark for Beer Company Analysis"
echo "=============================================="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install Homebrew first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "✅ Homebrew found"

# Install Java 11
echo "📦 Installing Java 11..."
brew install openjdk@11

# Set up Java environment
echo "🔧 Setting up Java environment..."
echo 'export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"' >> ~/.zshrc
echo 'export JAVA_HOME="/opt/homebrew/opt/openjdk@11"' >> ~/.zshrc

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install pyspark pandas numpy matplotlib plotly jupyter pyarrow

# Verify installations
echo "🔍 Verifying installations..."

# Check Java
if java -version 2>&1 | grep -q "openjdk version"; then
    echo "✅ Java installed successfully"
else
    echo "⚠️  Java installation may need manual verification"
fi

# Check PySpark
if python3 -c "import pyspark; print('PySpark version:', pyspark.__version__)" 2>/dev/null; then
    echo "✅ PySpark installed successfully"
else
    echo "❌ PySpark installation failed"
    exit 1
fi

echo ""
echo "🎉 Installation completed!"
echo ""
echo "Next steps:"
echo "1. Reload your shell: source ~/.zshrc"
echo "2. Test installation: python3 spark_hello_world.py"
echo "3. Initialize environment: python3 spark_init.py"
echo ""
echo "💡 If you encounter issues, check PYSPARK_SETUP.md for troubleshooting"