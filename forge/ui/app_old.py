"""Forge POC - Streamlit Frontend"""

import time
import streamlit as st
import requests
import json
import base64

# Configuration
API_URL = "http://localhost:8000"

# Forge Logo SVG
FORGE_LOGO_SVG = """
<svg width="180" height="50" viewBox="0 0 180 50" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="forgeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#FF6B35;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#F7931E;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#FFB347;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="anvilGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#4A5568;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#2D3748;stop-opacity:1" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- Anvil Base -->
  <path d="M8 38 L12 32 L36 32 L40 38 L8 38" fill="url(#anvilGrad)"/>
  <rect x="14" y="28" width="20" height="4" rx="1" fill="url(#anvilGrad)"/>
  
  <!-- Hammer -->
  <rect x="20" y="8" width="8" height="18" rx="2" fill="url(#anvilGrad)" transform="rotate(-30 24 17)"/>
  <rect x="18" y="4" width="12" height="8" rx="2" fill="url(#forgeGrad)" transform="rotate(-30 24 8)" filter="url(#glow)"/>
  
  <!-- Sparks -->
  <circle cx="32" cy="26" r="2" fill="#FF6B35" opacity="0.9">
    <animate attributeName="opacity" values="0.9;0.3;0.9" dur="1s" repeatCount="indefinite"/>
  </circle>
  <circle cx="38" cy="22" r="1.5" fill="#FFB347" opacity="0.8">
    <animate attributeName="opacity" values="0.8;0.2;0.8" dur="0.8s" repeatCount="indefinite"/>
  </circle>
  <circle cx="35" cy="18" r="1" fill="#F7931E" opacity="0.7">
    <animate attributeName="opacity" values="0.7;0.1;0.7" dur="1.2s" repeatCount="indefinite"/>
  </circle>
  
  <!-- Text -->
  <text x="52" y="34" font-family="'Segoe UI', Arial, sans-serif" font-size="28" font-weight="700" fill="#1a202c">
    <tspan fill="url(#forgeGrad)">F</tspan><tspan>ORGE</tspan>
  </text>
</svg>
"""

FORGE_LOGO_SMALL = """
<svg width="40" height="40" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="forgeGradSmall" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#FF6B35;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#F7931E;stop-opacity:1" />
    </linearGradient>
  </defs>
  <circle cx="24" cy="24" r="22" fill="#1a202c"/>
  <path d="M14 34 L17 30 L31 30 L34 34 L14 34" fill="#4A5568"/>
  <rect x="19" y="27" width="10" height="3" rx="1" fill="#4A5568"/>
  <rect x="21" y="14" width="6" height="12" rx="1" fill="#4A5568" transform="rotate(-25 24 20)"/>
  <rect x="19" y="11" width="10" height="6" rx="1" fill="url(#forgeGradSmall)" transform="rotate(-25 24 14)"/>
  <circle cx="32" cy="24" r="2" fill="#FF6B35" opacity="0.9"/>
  <circle cx="36" cy="20" r="1.5" fill="#FFB347" opacity="0.7"/>
</svg>
"""

# Page config
st.set_page_config(
    page_title="Forge - AI Endpoint Compliance",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Modern Dark Theme
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main Header */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 50%, #FFB347 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        font-size: 1.15rem;
        color: #718096;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Cards */
    .forge-card {
        background: linear-gradient(145deg, #ffffff 0%, #f7fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
    }
    
    .forge-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .forge-card-dark {
        background: linear-gradient(145deg, #1a202c 0%, #2d3748 100%);
        border: 1px solid #4a5568;
        color: white;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.35rem 1rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-completed { 
        background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
        color: white;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }
    .status-analyzing { 
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); 
        color: white;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
        animation: pulse 2s infinite;
    }
    .status-packaging { 
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); 
        color: white;
        box-shadow: 0 2px 4px rgba(139, 92, 246, 0.3);
        animation: pulse 2s infinite;
    }
    .status-pending { 
        background: linear-gradient(135deg, #6B7280 0%, #4B5563 100%); 
        color: white; 
    }
    .status-failed { 
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); 
        color: white;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
    }
    .status-needs_review { 
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); 
        color: white;
        box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Confidence Indicators */
    .confidence-high { color: #10B981; font-weight: 600; }
    .confidence-medium { color: #F59E0B; font-weight: 600; }
    .confidence-low { color: #EF4444; font-weight: 600; }
    
    /* Stat Cards */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.25rem;
        color: white;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
    }
    
    .stat-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        opacity: 0.9;
        margin-top: 0.25rem;
    }
    
    /* Upload Zone */
    .upload-zone {
        border: 2px dashed #cbd5e0;
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        background: linear-gradient(145deg, #f7fafc 0%, #edf2f7 100%);
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        border-color: #FF6B35;
        background: linear-gradient(145deg, #fff5f0 0%, #feebc8 100%);
    }
    
    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0;
    }
    
    /* Progress Steps */
    .step-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin: 0.25rem 0;
        font-size: 0.9rem;
    }
    
    .step-active {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white;
    }
    
    .step-complete {
        background: #10B981;
        color: white;
    }
    
    .step-pending {
        background: #e2e8f0;
        color: #718096;
    }
    
    /* Code blocks */
    .stCodeBlock {
        border-radius: 8px !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
    }
    
    /* Logo container */
    .logo-container {
        padding: 1rem 0;
        margin-bottom: 1rem;
    }
    
    /* Divider */
    .forge-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #4a5568 50%, transparent 100%);
        margin: 1.5rem 0;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Feature pills */
    .feature-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.25rem 0.75rem;
        background: rgba(255, 107, 53, 0.1);
        border: 1px solid rgba(255, 107, 53, 0.3);
        border-radius: 9999px;
        font-size: 0.75rem;
        color: #FF6B35;
        margin: 0.125rem;
    }
</style>
""", unsafe_allow_html=True)


def get_api_health():
    """Check if API is available."""
    try:
        response = requests.get(f"{API_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False


def upload_installer(file):
    """Upload an installer file to the API."""
    try:
        files = {"file": (file.name, file.getvalue(), "application/octet-stream")}
        response = requests.post(f"{API_URL}/packages/upload", files=files)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def get_job_status(job_id):
    """Get the status of a packaging job."""
    try:
        response = requests.get(f"{API_URL}/packages/{job_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_all_jobs():
    """Get all packaging jobs."""
    try:
        response = requests.get(f"{API_URL}/packages")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


def get_knowledge_stats():
    """Get knowledge base statistics."""
    try:
        response = requests.get(f"{API_URL}/knowledge/stats")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}


def search_knowledge(query):
    """Search the knowledge base."""
    try:
        response = requests.get(f"{API_URL}/knowledge/search", params={"query": query})
        if response.status_code == 200:
            return response.json()
        return {"results": []}
    except:
        return {"results": []}


def render_sidebar():
    """Render the sidebar."""
    with st.sidebar:
        # Logo
        st.markdown(f'<div class="logo-container">{FORGE_LOGO_SVG}</div>', unsafe_allow_html=True)
        st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
        
        # Tagline
        st.markdown("""
        <div style="color: #a0aec0; font-size: 0.85rem; margin-bottom: 1rem;">
            AI-Powered Endpoint<br/>Compliance Automation
        </div>
        """, unsafe_allow_html=True)
        
        # API Status
        api_healthy = get_api_health()
        if api_healthy:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; 
                        background: rgba(16, 185, 129, 0.1); border-radius: 8px; margin-bottom: 1rem;">
                <span style="color: #10B981;">●</span>
                <span style="color: #10B981; font-size: 0.85rem;">API Connected</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; 
                        background: rgba(239, 68, 68, 0.1); border-radius: 8px; margin-bottom: 1rem;">
                <span style="color: #EF4444;">●</span>
                <span style="color: #EF4444; font-size: 0.85rem;">API Offline</span>
            </div>
            """, unsafe_allow_html=True)
            st.code("uvicorn forge.api.main:app --reload", language="bash")
        
        st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
        
        # Knowledge Base Stats
        st.markdown('<div class="section-header">📚 Knowledge Base</div>', unsafe_allow_html=True)
        stats = get_knowledge_stats()
        if stats:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number">{stats.get("total_packages", 0)}</div>
                    <div class="stat-label">Packages</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="stat-card" style="background: linear-gradient(135deg, #10B981 0%, #059669 100%);">
                    <div class="stat-number">{stats.get("total_commands", 0)}</div>
                    <div class="stat-label">Commands</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
        
        # Navigation
        st.markdown('<div class="section-header">Navigation</div>', unsafe_allow_html=True)
        page = st.radio(
            "Go to",
            ["🏠 Upload", "📦 Jobs", "🔍 Search", "📊 Dashboard"],
            label_visibility="collapsed"
        )
        
        st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
        
        # Features
        st.markdown('<div class="section-header">✨ Features</div>', unsafe_allow_html=True)
        st.markdown("""
        <div>
            <span class="feature-pill">🤖 AI Analysis</span>
            <span class="feature-pill">🛡️ WDAC Policy</span>
            <span class="feature-pill">📦 Auto Package</span>
            <span class="feature-pill">🔍 RAG Search</span>
        </div>
        """, unsafe_allow_html=True)
        
        return page


def render_upload_page():
    """Render the main upload page."""
    
    # Hero Section with Logo
    col_logo, col_title = st.columns([1, 10])
    with col_logo:
        st.markdown(FORGE_LOGO_SMALL, unsafe_allow_html=True)
    with col_title:
        st.markdown("""
        <h1 class="main-header">Forge</h1>
        <p class="sub-header" style="margin-top: -10px;">Drop an installer. Get a signed, policy-ready package in minutes.</p>
        """, unsafe_allow_html=True)
    
    # Process Steps
    st.markdown("""
    <div style="display: flex; gap: 1rem; margin: 1.5rem 0; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 150px; text-align: center; padding: 1rem; background: linear-gradient(145deg, #fff5f0 0%, #feebc8 100%); border-radius: 12px; border: 1px solid #fed7aa;">
            <div style="font-size: 1.5rem;">📤</div>
            <div style="font-weight: 600; color: #c2410c;">1. Upload</div>
            <div style="font-size: 0.75rem; color: #9a3412;">Drop installer</div>
        </div>
        <div style="flex: 1; min-width: 150px; text-align: center; padding: 1rem; background: linear-gradient(145deg, #eff6ff 0%, #dbeafe 100%); border-radius: 12px; border: 1px solid #bfdbfe;">
            <div style="font-size: 1.5rem;">🤖</div>
            <div style="font-weight: 600; color: #1d4ed8;">2. Analyze</div>
            <div style="font-size: 0.75rem; color: #1e40af;">AI discovers switches</div>
        </div>
        <div style="flex: 1; min-width: 150px; text-align: center; padding: 1rem; background: linear-gradient(145deg, #f5f3ff 0%, #ede9fe 100%); border-radius: 12px; border: 1px solid #c4b5fd;">
            <div style="font-size: 1.5rem;">📦</div>
            <div style="font-weight: 600; color: #6d28d9;">3. Package</div>
            <div style="font-size: 0.75rem; color: #5b21b6;">Generate scripts</div>
        </div>
        <div style="flex: 1; min-width: 150px; text-align: center; padding: 1rem; background: linear-gradient(145deg, #ecfdf5 0%, #d1fae5 100%); border-radius: 12px; border: 1px solid #a7f3d0;">
            <div style="font-size: 1.5rem;">🛡️</div>
            <div style="font-weight: 600; color: #047857;">4. Secure</div>
            <div style="font-size: 0.75rem; color: #065f46;">WDAC policy</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Upload Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📤 Upload Installer")
        
        uploaded_file = st.file_uploader(
            "Drag and drop your installer here",
            type=["msi", "exe", "msix"],
            help="Supported formats: MSI, EXE, MSIX"
        )
        
        if uploaded_file:
            st.markdown(f"""
            <div class="forge-card" style="margin: 1rem 0;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="font-size: 2rem;">📁</div>
                    <div>
                        <div style="font-weight: 600; color: #1a202c;">{uploaded_file.name}</div>
                        <div style="font-size: 0.85rem; color: #718096;">{uploaded_file.size / 1024:.1f} KB • Ready to process</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Start Packaging", type="primary", use_container_width=True):
                with st.spinner("Uploading and analyzing..."):
                    result = upload_installer(uploaded_file)
                    
                    if result:
                        st.session_state.current_job_id = result["id"]
                        st.success(f"Job created: **{result['id']}**")
                        st.rerun()
    
    with col2:
        st.markdown("### ⚡ Quick Stats")
        
        jobs = get_all_jobs()
        completed = len([j for j in jobs if j["status"] == "completed"])
        pending = len([j for j in jobs if j["status"] in ["pending", "analyzing", "packaging"]])
        needs_review = len([j for j in jobs if j["status"] == "needs_review"])
        
        st.markdown(f"""
        <div class="forge-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #718096;">Completed</span>
                <span style="font-size: 1.5rem; font-weight: 700; color: #10B981;">{completed}</span>
            </div>
        </div>
        <div class="forge-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #718096;">In Progress</span>
                <span style="font-size: 1.5rem; font-weight: 700; color: #3B82F6;">{pending}</span>
            </div>
        </div>
        <div class="forge-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #718096;">Needs Review</span>
                <span style="font-size: 1.5rem; font-weight: 700; color: #F59E0B;">{needs_review}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        stats = get_knowledge_stats()
        st.markdown(f"""
        <div class="forge-card forge-card-dark">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #a0aec0;">Knowledge Base</span>
                <span style="font-size: 1.5rem; font-weight: 700; color: #FF6B35;">{stats.get('total_packages', 0)}</span>
            </div>
            <div style="font-size: 0.75rem; color: #718096; margin-top: 0.25rem;">apps indexed</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Current Job Status
    if "current_job_id" in st.session_state:
        render_job_details(st.session_state.current_job_id)


def render_job_details(job_id):
    """Render details for a specific job."""
    st.divider()
    
    job = get_job_status(job_id)
    if not job:
        st.error("Job not found")
        return
    
    # Header with status
    status_icons = {
        "completed": "✅",
        "analyzing": "🔍",
        "packaging": "📦",
        "validating": "🛡️",
        "pending": "⏳",
        "failed": "❌",
        "needs_review": "⚠️",
    }
    
    status_class = f"status-{job['status']}"
    status_icon = status_icons.get(job["status"], "⏳")
    
    st.markdown(f"""
    <div class="forge-card" style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <div>
                <div style="font-size: 0.75rem; color: #718096; text-transform: uppercase; letter-spacing: 0.1em;">Job ID</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #1a202c; font-family: monospace;">{job_id}</div>
                <div style="color: #718096; margin-top: 0.25rem;">{job['filename']}</div>
            </div>
            <div>
                <span class="status-badge {status_class}">{status_icon} {job["status"].replace("_", " ").upper()}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh if still processing
    if job["status"] in ["pending", "analyzing", "packaging", "validating"]:
        time.sleep(2)
        st.rerun()
    
    # Show results
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Metadata")
        if job.get("metadata"):
            meta = job["metadata"]
            st.markdown(f"""
            <div class="forge-card">
                <table style="width: 100%; font-size: 0.9rem;">
                    <tr><td style="color: #718096; padding: 0.25rem 0;">Product</td><td style="font-weight: 600;">{meta.get("product_name", "Unknown")}</td></tr>
                    <tr><td style="color: #718096; padding: 0.25rem 0;">Version</td><td style="font-weight: 600;">{meta.get("product_version", "Unknown")}</td></tr>
                    <tr><td style="color: #718096; padding: 0.25rem 0;">Manufacturer</td><td style="font-weight: 600;">{meta.get("manufacturer", "Unknown")}</td></tr>
                    <tr><td style="color: #718096; padding: 0.25rem 0;">Type</td><td><span class="feature-pill">{meta.get("installer_type", "Unknown").upper()}</span></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Extracting metadata...")
    
    with col2:
        st.markdown("#### 🤖 AI Analysis")
        if job.get("analysis"):
            analysis = job["analysis"]
            
            # Confidence indicator
            confidence = analysis.get("confidence", 0)
            if confidence >= 0.8:
                conf_color = "#10B981"
                conf_bg = "rgba(16, 185, 129, 0.1)"
                conf_label = "High"
            elif confidence >= 0.6:
                conf_color = "#F59E0B"
                conf_bg = "rgba(245, 158, 11, 0.1)"
                conf_label = "Medium"
            else:
                conf_color = "#EF4444"
                conf_bg = "rgba(239, 68, 68, 0.1)"
                conf_label = "Low"
            
            st.markdown(f"""
            <div class="forge-card">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <div style="background: {conf_bg}; padding: 0.75rem 1rem; border-radius: 8px; text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: {conf_color};">{confidence:.0%}</div>
                        <div style="font-size: 0.7rem; color: {conf_color}; text-transform: uppercase;">{conf_label} Confidence</div>
                    </div>
                    <div style="flex: 1; font-size: 0.85rem; color: #4a5568;">
                        {analysis.get('reasoning', '')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Similar packages
            if analysis.get("similar_packages"):
                st.markdown("**📚 Similar in Knowledge Base:**")
                for pkg in analysis["similar_packages"][:3]:
                    st.markdown(f"<span class='feature-pill'>📦 {pkg}</span>", unsafe_allow_html=True)
        else:
            st.info("AI analysis in progress...")
    
    # Install Command
    if job.get("analysis") and job["analysis"].get("install_command"):
        st.markdown("#### 💻 Install Command")
        st.code(job["analysis"]["install_command"], language="powershell")
        
        # Silent Switches as pills
        switches = job["analysis"].get("silent_switches", [])
        if switches:
            switch_pills = " ".join([f'<span class="feature-pill">{s}</span>' for s in switches])
            st.markdown(f"**Switches:** {switch_pills}", unsafe_allow_html=True)
    
    # WDAC Policy
    if job.get("policy"):
        st.markdown("#### 🛡️ WDAC Policy Generated")
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.markdown(f"""
            <div class="forge-card" style="background: linear-gradient(145deg, #ecfdf5 0%, #d1fae5 100%); border-color: #a7f3d0;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 1.5rem;">🛡️</span>
                    <div>
                        <div style="font-weight: 600; color: #065f46;">{job["policy"].get("policy_name", "Policy")}</div>
                        <div style="font-size: 0.8rem; color: #047857;">Hash-based allowlist rule generated</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            with st.expander("View XML"):
                st.code(job["policy"].get("policy_xml", ""), language="xml")
    
    # Known Issues
    if job.get("analysis") and job["analysis"].get("known_issues"):
        st.markdown("#### ⚠️ Known Issues")
        for issue in job["analysis"]["known_issues"]:
            st.warning(issue)
    
    # Error
    if job.get("error_message"):
        st.error(f"**Error:** {job['error_message']}")


def render_jobs_page():
    """Render the jobs list page."""
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
        {FORGE_LOGO_SMALL}
        <h2 style="margin: 0;">All Packaging Jobs</h2>
    </div>
    """, unsafe_allow_html=True)
    
    jobs = get_all_jobs()
    
    if not jobs:
        st.markdown("""
        <div class="forge-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📦</div>
            <div style="font-size: 1.25rem; font-weight: 600; color: #1a202c;">No jobs yet</div>
            <div style="color: #718096;">Upload an installer to get started!</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Filter by status
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "completed", "analyzing", "pending", "failed", "needs_review"]
        )
    
    with col2:
        sort_order = st.selectbox("Sort by", ["Newest first", "Oldest first"])
    
    if status_filter != "All":
        jobs = [j for j in jobs if j["status"] == status_filter]
    
    if sort_order == "Oldest first":
        jobs = list(reversed(jobs))
    
    st.markdown(f"**{len(jobs)} job(s)**")
    
    # Display jobs as cards
    for job in jobs:
        status_icons = {
            "completed": "✅",
            "analyzing": "🔍",
            "packaging": "📦",
            "pending": "⏳",
            "failed": "❌",
            "needs_review": "⚠️",
        }
        icon = status_icons.get(job["status"], "⏳")
        
        with st.expander(f"{icon} **{job['filename']}** — `{job['id']}`", expanded=False):
            render_job_details(job["id"])


def render_search_page():
    """Render the knowledge base search page."""
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
        {FORGE_LOGO_SMALL}
        <h2 style="margin: 0;">Search Knowledge Base</h2>
    </div>
    <p class="sub-header">Find similar packages or search for specific applications in our indexed database.</p>
    """, unsafe_allow_html=True)
    
    query = st.text_input("🔍 Search", placeholder="e.g., Chrome, Adobe, silent install, /qn")
    
    if query:
        with st.spinner("Searching..."):
            results = search_knowledge(query)
        
        if results.get("results"):
            st.success(f"Found **{len(results['results'])}** matching packages")
            
            for r in results["results"]:
                confidence = r.get("confidence", 0)
                if confidence >= 0.8:
                    conf_color = "#10B981"
                elif confidence >= 0.6:
                    conf_color = "#F59E0B"
                else:
                    conf_color = "#EF4444"
                
                st.markdown(f"""
                <div class="forge-card" style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem;">
                        <div style="flex: 1;">
                            <div style="font-weight: 700; font-size: 1.1rem; color: #1a202c;">{r.get('product_name', r.get('filename', 'Unknown'))}</div>
                            <div style="color: #718096; font-size: 0.85rem; margin: 0.25rem 0;">
                                {r.get('manufacturer', 'Unknown')} • v{r.get('version', 'Unknown')}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.25rem; font-weight: 700; color: {conf_color};">{confidence:.0%}</div>
                            <div style="font-size: 0.7rem; color: #718096;">confidence</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if r.get("install_command"):
                    st.code(r["install_command"], language="powershell")
        else:
            st.info("No results found. Try a different search term.")
    else:
        # Show some stats
        stats = get_knowledge_stats()
        st.markdown(f"""
        <div style="display: flex; gap: 1rem; margin-top: 2rem;">
            <div class="forge-card" style="flex: 1; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 700; color: #FF6B35;">{stats.get('total_packages', 0)}</div>
                <div style="color: #718096;">Indexed Applications</div>
            </div>
            <div class="forge-card" style="flex: 1; text-align: center;">
                <div style="font-size: 2.5rem; font-weight: 700; color: #3B82F6;">{stats.get('total_commands', 0)}</div>
                <div style="color: #718096;">Known Commands</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_dashboard():
    """Render a dashboard overview."""
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
        {FORGE_LOGO_SMALL}
        <h2 style="margin: 0;">Dashboard</h2>
    </div>
    <p class="sub-header">Overview of your packaging operations</p>
    """, unsafe_allow_html=True)
    
    jobs = get_all_jobs()
    stats = get_knowledge_stats()
    
    # Summary cards
    completed = len([j for j in jobs if j["status"] == "completed"])
    pending = len([j for j in jobs if j["status"] in ["pending", "analyzing", "packaging"]])
    needs_review = len([j for j in jobs if j["status"] == "needs_review"])
    failed = len([j for j in jobs if j["status"] == "failed"])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); padding: 1.5rem; border-radius: 12px; color: white; text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 700;">{completed}</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">Completed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); padding: 1.5rem; border-radius: 12px; color: white; text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 700;">{pending}</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">In Progress</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); padding: 1.5rem; border-radius: 12px; color: white; text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 700;">{needs_review}</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">Needs Review</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #6B7280 0%, #4B5563 100%); padding: 1.5rem; border-radius: 12px; color: white; text-align: center;">
            <div style="font-size: 2.5rem; font-weight: 700;">{stats.get('total_packages', 0)}</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">Knowledge Base</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Recent Jobs
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.markdown("### 📋 Recent Jobs")
        if jobs:
            for job in jobs[:5]:
                status_icons = {"completed": "✅", "analyzing": "🔍", "pending": "⏳", "failed": "❌", "needs_review": "⚠️"}
                icon = status_icons.get(job["status"], "⏳")
                st.markdown(f"""
                <div class="forge-card" style="margin-bottom: 0.5rem; padding: 0.75rem 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="margin-right: 0.5rem;">{icon}</span>
                            <span style="font-weight: 500;">{job['filename']}</span>
                        </div>
                        <code style="font-size: 0.8rem; color: #718096;">{job['id']}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No jobs yet")
    
    with col_b:
        st.markdown("### 💡 Quick Actions")
        if st.button("📤 Upload New", use_container_width=True):
            st.session_state.nav_page = "🏠 Upload"
            st.rerun()
        if st.button("🔍 Search KB", use_container_width=True):
            st.session_state.nav_page = "🔍 Search"
            st.rerun()


# Main app
def main():
    page = render_sidebar()
    
    if "🏠 Upload" in page:
        render_upload_page()
    elif "📦 Jobs" in page:
        render_jobs_page()
    elif "🔍 Search" in page:
        render_search_page()
    elif "📊 Dashboard" in page:
        render_dashboard()


if __name__ == "__main__":
    main()
