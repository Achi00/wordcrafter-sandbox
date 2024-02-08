echo "Checking for package.json..."
if [ -f "package.json" ]; then
  echo "package.json found. Installing dependencies..."
  npm install --verbose
  echo "Dependencies installed."
else
  echo "No package.json found. Skipping dependency installation."
fi

echo "Executing script: $1"
node "$1"
