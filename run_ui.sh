#!/bin/bash

# Start the Interview Agent UI with Streamlit

echo "Starting NCO Interview Agent UI..."
echo ""

# Check if streamlit is installed
python3 -c "import streamlit" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

echo "Opening Interview Agent in your browser..."
python3 -m streamlit run app.py
