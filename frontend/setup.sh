#!/bin/bash

echo "🚀 Instagram Downloader - React Frontend Setup"
echo "============================================="
echo ""

# Check Node.js
echo "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found! Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "✅ Node.js found: $NODE_VERSION"
echo ""

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed successfully!"
echo ""

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "📝 Creating .env.local file..."
    cp .env.example .env.local
    echo "✅ Created .env.local (update with your backend URL)"
else
    echo "✅ .env.local already exists"
fi
echo ""

# Done
echo "🎉 Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env.local and set your backend URL"
echo "2. Run: npm run dev"
echo "3. Open: http://localhost:3000"
echo ""
echo "To deploy to Vercel:"
echo "1. Run: npm i -g vercel"
echo "2. Run: vercel"
echo ""
echo "Happy coding! 💻✨"
