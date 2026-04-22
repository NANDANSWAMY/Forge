# Hugging Face Spaces entry point
# This file imports and runs the main Streamlit app

import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main app
from forge.ui.app import *
