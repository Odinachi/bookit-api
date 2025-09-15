#!/bin/bash

# Test script for the booking service API
echo "🧪 Running Booking Service Tests"
echo "================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "💡 Consider running: source .venv/bin/activate"
fi

# Install test dependencies if needed
echo "📦 Installing test dependencies..."
pip install -r requirements-test.txt

# Set Python path to include current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo ""
echo "🏃‍♂️ Running unit tests..."
echo "=========================="

# Run tests without coverage (simpler setup)
PYTHONPATH="$(pwd)" pytest tests/ -v --tb=short

TEST_RESULT=$?

echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ All tests passed successfully!"
else
    echo "❌ Some tests failed. Check the output above for details."
fi

echo ""
echo "🔧 Test Summary:"
echo "================"
echo "• Model tests: Unit tests for Pydantic models"
echo "• Service tests: Business logic with mocked dependencies"
echo "• Logic tests: Core algorithms and validation rules"
echo "• Error handling: Edge cases and error scenarios"
echo ""
echo "🚀 To run specific test categories:"
echo "   PYTHONPATH=\"\$(pwd)\" pytest tests/test_models.py -v"
echo "   PYTHONPATH=\"\$(pwd)\" pytest tests/test_services.py -v"
echo "   PYTHONPATH=\"\$(pwd)\" pytest tests/test_repositories.py -v"
echo "   PYTHONPATH=\"\$(pwd)\" pytest tests/test_api.py -v"

exit $TEST_RESULT