"""Forge POC - Streamlit Frontend - Premium Edition"""

import time
import random
import math
from datetime import datetime, timedelta
import streamlit as st
import streamlit.components.v1 as components
import requests
from streamlit_autorefresh import st_autorefresh

# Configuration
API_URL = "http://localhost:8000"

# Auto Demo Configuration
AUTO_DEMO_PAGES = ["🏠  Upload", "📦  Jobs", "📊  Dashboard"]
AUTO_DEMO_INTERVAL = 10  # default seconds per page
# Per-page timing (seconds)
AUTO_DEMO_PAGE_TIMES = {
    "🏠  Upload": 10,
    "📦  Jobs": 14,
    "📊  Dashboard": 6,
}

# VC Demo Captions - Story for each page
DEMO_CAPTIONS = {
    "🏠  Upload": {"headline": "Zero-Touch Packaging", "subtext": "Drop any installer. Get enterprise-ready in seconds."},
    "📦  Jobs": {"headline": "AI-Powered Analysis", "subtext": "Silent switches discovered automatically. 94% accuracy."},
    "💰  Impact": {"headline": "$4.2B Market", "subtext": "50,000+ IT teams. Massive efficiency gains."},
    "📊  Dashboard": {"headline": "156 Hours Saved", "subtext": "Automated compliance at enterprise scale."},
    "🔍  Search": {"headline": "1,800+ Commands", "subtext": "RAG-powered knowledge base grows with every package."},
}

# Demo/Mock Data for showcase
DEMO_MODE = True  # Set to False when connected to real backend

MOCK_JOBS = [
    {"id": "pkg-7zip-2301", "filename": "7zip_23.01_x64.msi", "status": "completed", 
     "metadata": {"product_name": "7-Zip", "product_version": "23.01", "manufacturer": "Igor Pavlov", "installer_type": "msi"},
     "analysis": {"confidence": 0.95, "install_command": "msiexec /i 7zip_23.01_x64.msi /qn", "silent_switches": ["/qn"], "reasoning": "MSI installer with standard silent switches"},
     "policy": {"policy_name": "7-Zip_23.01_WDAC", "policy_xml": "<SignerRule>...</SignerRule>"}},
    {"id": "pkg-chrome-120", "filename": "Chrome_120.0_Enterprise.msi", "status": "completed",
     "metadata": {"product_name": "Google Chrome", "product_version": "120.0", "manufacturer": "Google LLC", "installer_type": "msi"},
     "analysis": {"confidence": 0.98, "install_command": "msiexec /i Chrome_120.0_Enterprise.msi /qn /norestart", "silent_switches": ["/qn", "/norestart"], "reasoning": "Enterprise MSI with verified silent parameters"},
     "policy": {"policy_name": "Chrome_120_WDAC", "policy_xml": "<SignerRule>...</SignerRule>"}},
    {"id": "pkg-vscode-185", "filename": "VSCode_1.85_x64.exe", "status": "completed",
     "metadata": {"product_name": "Visual Studio Code", "product_version": "1.85", "manufacturer": "Microsoft Corporation", "installer_type": "exe"},
     "analysis": {"confidence": 0.92, "install_command": "VSCode_1.85_x64.exe /VERYSILENT /NORESTART /MERGETASKS=!runcode", "silent_switches": ["/VERYSILENT", "/NORESTART"], "reasoning": "Inno Setup installer detected"},
     "policy": {"policy_name": "VSCode_1.85_WDAC", "policy_xml": "<SignerRule>...</SignerRule>"}},
    {"id": "pkg-firefox-121", "filename": "Firefox_121.0_Setup.exe", "status": "needs_review",
     "metadata": {"product_name": "Mozilla Firefox", "product_version": "121.0", "manufacturer": "Mozilla", "installer_type": "exe"},
     "analysis": {"confidence": 0.72, "install_command": "Firefox_121.0_Setup.exe -ms", "silent_switches": ["-ms"], "reasoning": "Mozilla installer - verify INI configuration", "known_issues": ["May require mozilla.cfg for enterprise settings"]},
     "policy": None},
    {"id": "pkg-vlc-320", "filename": "VLC_3.0.20_Setup.exe", "status": "analyzing",
     "metadata": {"product_name": "VLC Media Player", "product_version": "3.0.20", "manufacturer": "VideoLAN", "installer_type": "exe"},
     "analysis": None, "policy": None},
    {"id": "pkg-notepad-85", "filename": "NotepadPlusPlus_8.5_Setup.exe", "status": "completed",
     "metadata": {"product_name": "Notepad++", "product_version": "8.5", "manufacturer": "Don Ho", "installer_type": "exe"},
     "analysis": {"confidence": 0.89, "install_command": "NotepadPlusPlus_8.5_Setup.exe /S", "silent_switches": ["/S"], "reasoning": "NSIS installer with standard silent switch"},
     "policy": {"policy_name": "NotepadPP_8.5_WDAC", "policy_xml": "<SignerRule>...</SignerRule>"}},
    {"id": "pkg-zoom-59", "filename": "Zoom_5.9_x64.msi", "status": "completed",
     "metadata": {"product_name": "Zoom", "product_version": "5.9", "manufacturer": "Zoom Video Communications", "installer_type": "msi"},
     "analysis": {"confidence": 0.94, "install_command": "msiexec /i Zoom_5.9_x64.msi /qn /norestart ZoomAutoUpdate=0", "silent_switches": ["/qn", "/norestart"], "reasoning": "MSI with auto-update disabled for enterprise"},
     "policy": {"policy_name": "Zoom_5.9_WDAC", "policy_xml": "<SignerRule>...</SignerRule>"}},
    {"id": "pkg-teams-new", "filename": "Teams_24.1_x64.msix", "status": "pending",
     "metadata": None, "analysis": None, "policy": None},
]

MOCK_STATS = {
    "total_packages": 247,
    "total_commands": 1892,
    "packages_this_week": 34,
    "success_rate": 94.2,
    "avg_processing_time": 2.3,
    "time_saved_hours": 156,
    "top_manufacturers": [("Microsoft", 67), ("Google", 23), ("Adobe", 19), ("Mozilla", 12), ("Other", 126)],
    "installer_types": {"msi": 142, "exe": 89, "msix": 16},
    "weekly_trend": [28, 31, 25, 42, 38, 34, 29],
    "confidence_distribution": {"high": 78, "medium": 15, "low": 7}
}

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="Forge | Enterprise Endpoint Compliance Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS - Modern Glass Design
st.markdown("""
<style>
    /* ===== FONTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* ===== ROOT VARIABLES ===== */
    :root {
        --forge-orange: #FF6B35;
        --forge-orange-light: #FF8C5A;
        --forge-orange-dark: #E55A2B;
        --forge-gold: #FFB347;
        --forge-dark: #0F1419;
        --forge-darker: #080B0F;
        --forge-card: rgba(255, 255, 255, 0.03);
        --forge-card-border: rgba(255, 255, 255, 0.08);
        --forge-text: #E7E9EA;
        --forge-text-muted: #71767B;
        --forge-success: #00BA7C;
        --forge-warning: #FFD93D;
        --forge-error: #F4212E;
        --forge-info: #1D9BF0;
        --glass-bg: rgba(15, 20, 25, 0.8);
        --glass-border: rgba(255, 255, 255, 0.1);
    }
    
    /* ===== GLOBAL STYLES ===== */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #0F1419 0%, #1A1F25 50%, #0F1419 100%);
        background-attachment: fixed;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(ellipse at 20% 20%, rgba(255, 107, 53, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(255, 179, 71, 0.05) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(29, 155, 240, 0.03) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: var(--forge-text);
    }
    
    p, span, div {
        color: var(--forge-text);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        line-height: 1.1;
        margin: 0;
        background: linear-gradient(135deg, #FF6B35 0%, #FFB347 50%, #FF6B35 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 3s linear infinite;
    }
    
    @keyframes shimmer {
        0% { background-position: 0% center; }
        100% { background-position: 200% center; }
    }
    
    .hero-subtitle {
        font-size: 1.15rem;
        font-weight: 400;
        color: var(--forge-text-muted);
        margin-top: 0.75rem;
        letter-spacing: -0.01em;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .hero-logo-container {
        margin-bottom: 1.25rem;
        filter: drop-shadow(0 8px 24px rgba(255, 107, 53, 0.25));
    }
    
    .hero-logo {
        animation: logo-pulse 4s ease-in-out infinite;
    }
    
    @keyframes logo-pulse {
        0%, 100% { transform: scale(1); filter: drop-shadow(0 0 0 rgba(255, 107, 53, 0)); }
        50% { transform: scale(1.02); filter: drop-shadow(0 0 20px rgba(255, 107, 53, 0.3)); }
    }
    
    .hero-badges {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-top: 1.5rem;
        flex-wrap: wrap;
    }
    
    .hero-badge {
        padding: 0.5rem 1rem;
        background: rgba(255, 107, 53, 0.1);
        border: 1px solid rgba(255, 107, 53, 0.2);
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--forge-orange);
        letter-spacing: 0.02em;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--forge-text);
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-title::before {
        content: '';
        width: 4px;
        height: 24px;
        background: linear-gradient(180deg, var(--forge-orange) 0%, var(--forge-gold) 100%);
        border-radius: 2px;
    }
    
    /* ===== GLASS CARDS ===== */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 1.75rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.1) 50%, transparent 100%);
    }
    
    .glass-card:hover {
        border-color: rgba(255, 107, 53, 0.3);
        transform: translateY(-4px);
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.3),
            0 0 40px rgba(255, 107, 53, 0.1);
    }
    
    .glass-card-sm {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        transition: all 0.3s ease;
    }
    
    .glass-card-sm:hover {
        border-color: rgba(255, 107, 53, 0.2);
    }
    
    /* ===== METRIC CARDS ===== */
    .metric-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--metric-color, var(--forge-orange));
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .metric-value {
        font-size: 2.75rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--forge-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    /* ===== STATUS BADGES ===== */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border: 1px solid transparent;
    }
    
    .badge-success {
        background: rgba(0, 186, 124, 0.15);
        border-color: rgba(0, 186, 124, 0.3);
        color: var(--forge-success);
    }
    
    .badge-warning {
        background: rgba(255, 217, 61, 0.15);
        border-color: rgba(255, 217, 61, 0.3);
        color: var(--forge-warning);
    }
    
    .badge-error {
        background: rgba(244, 33, 46, 0.15);
        border-color: rgba(244, 33, 46, 0.3);
        color: var(--forge-error);
    }
    
    .badge-info {
        background: rgba(29, 155, 240, 0.15);
        border-color: rgba(29, 155, 240, 0.3);
        color: var(--forge-info);
    }
    
    .badge-processing {
        background: rgba(139, 92, 246, 0.15);
        border-color: rgba(139, 92, 246, 0.3);
        color: #A78BFA;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    /* ===== UPLOAD ZONE ===== */
    .upload-zone {
        border: 2px dashed rgba(255, 107, 53, 0.3);
        border-radius: 24px;
        padding: 4rem 2rem;
        text-align: center;
        background: linear-gradient(145deg, rgba(255, 107, 53, 0.02) 0%, rgba(255, 179, 71, 0.02) 100%);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .upload-zone::before {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at center, rgba(255, 107, 53, 0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .upload-zone:hover {
        border-color: var(--forge-orange);
        background: linear-gradient(145deg, rgba(255, 107, 53, 0.05) 0%, rgba(255, 179, 71, 0.03) 100%);
        transform: scale(1.01);
    }
    
    .upload-zone:hover::before {
        opacity: 1;
    }
    
    .upload-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        display: block;
    }
    
    .upload-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--forge-text);
        margin-bottom: 0.5rem;
    }
    
    .upload-subtitle {
        font-size: 0.9rem;
        color: var(--forge-text-muted);
    }
    
    /* ===== PROCESS STEPS ===== */
    .process-container {
        display: flex;
        gap: 1rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .process-step {
        flex: 1;
        min-width: 140px;
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem 1rem;
        text-align: center;
        position: relative;
        transition: all 0.3s ease;
    }
    
    .process-step:hover {
        border-color: var(--step-color, var(--forge-orange));
        transform: translateY(-4px);
    }
    
    .process-step::after {
        content: '';
        position: absolute;
        top: 50%;
        right: -0.75rem;
        transform: translateY(-50%);
        width: 0;
        height: 0;
        border-top: 8px solid transparent;
        border-bottom: 8px solid transparent;
        border-left: 8px solid var(--glass-border);
    }
    
    .process-step:last-child::after {
        display: none;
    }
    
    .step-number {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, var(--step-color, var(--forge-orange)) 0%, var(--step-color-end, var(--forge-gold)) 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.75rem;
        font-weight: 700;
        font-size: 0.9rem;
        color: white;
    }
    
    .step-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .step-title {
        font-weight: 600;
        font-size: 0.9rem;
        color: var(--forge-text);
        margin-bottom: 0.25rem;
    }
    
    .step-desc {
        font-size: 0.75rem;
        color: var(--forge-text-muted);
    }
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A0D10 0%, #0F1419 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    
    .sidebar-logo {
        padding: 2rem 1.5rem;
        text-align: center;
        border-bottom: 1px solid rgba(255, 107, 53, 0.15);
        margin-bottom: 1.5rem;
        background: linear-gradient(180deg, rgba(255, 107, 53, 0.03) 0%, transparent 100%);
    }
    
    .forge-logo-mark {
        margin-bottom: 1rem;
        filter: drop-shadow(0 4px 12px rgba(255, 107, 53, 0.2));
    }
    
    .forge-logo-mark svg {
        transition: transform 0.3s ease, filter 0.3s ease;
    }
    
    .forge-logo-mark:hover svg {
        transform: scale(1.05);
        filter: drop-shadow(0 6px 20px rgba(255, 107, 53, 0.35));
    }
    
    .sidebar-brand {
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: 0.2em;
        background: linear-gradient(135deg, #FF6B35 0%, #FFB347 50%, #FF6B35 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .sidebar-tagline {
        font-size: 0.7rem;
        color: var(--forge-text);
        letter-spacing: 0.15em;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    .sidebar-tagline-sub {
        font-size: 0.65rem;
        color: var(--forge-text-muted);
        letter-spacing: 0.08em;
        font-weight: 400;
    }
    
    .sidebar-section {
        padding: 0 1rem;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-section-title {
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--forge-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 0.75rem;
        padding-left: 0.5rem;
    }
    
    /* ===== NAV ITEMS ===== */
    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.875rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.375rem;
        cursor: pointer;
        transition: all 0.2s ease;
        color: var(--forge-text-muted);
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    .nav-item:hover {
        background: rgba(255, 255, 255, 0.05);
        color: var(--forge-text);
    }
    
    .nav-item-active {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.15) 0%, rgba(255, 179, 71, 0.1) 100%);
        color: var(--forge-orange);
        border: 1px solid rgba(255, 107, 53, 0.2);
    }
    
    .nav-icon {
        font-size: 1.1rem;
        width: 24px;
        text-align: center;
    }
    
    /* ===== STATUS INDICATOR ===== */
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.5rem;
    }
    
    .status-dot-online {
        background: var(--forge-success);
        box-shadow: 0 0 8px var(--forge-success);
    }
    
    .status-dot-offline {
        background: var(--forge-error);
        box-shadow: 0 0 8px var(--forge-error);
    }
    
    /* ===== CODE BLOCKS ===== */
    .stCodeBlock {
        border-radius: 12px !important;
        border: 1px solid var(--glass-border) !important;
    }
    
    code {
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--forge-orange) 0%, var(--forge-orange-dark) 100%);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(255, 107, 53, 0.3);
    }
    
    /* ===== PROGRESS BAR ===== */
    .confidence-bar {
        height: 6px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .confidence-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.5s ease;
    }
    
    /* ===== PILLS ===== */
    .pill {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.875rem;
        background: rgba(255, 107, 53, 0.1);
        border: 1px solid rgba(255, 107, 53, 0.2);
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--forge-orange);
        margin: 0.25rem;
        transition: all 0.2s ease;
    }
    
    .pill:hover {
        background: rgba(255, 107, 53, 0.2);
    }
    
    /* ===== DIVIDER ===== */
    .forge-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.1) 50%, transparent 100%);
        margin: 1.5rem 0;
        border: none;
    }
    
    /* ===== ANIMATIONS ===== */
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(255, 107, 53, 0.3); }
        50% { box-shadow: 0 0 40px rgba(255, 107, 53, 0.5); }
    }
    
    .animate-float {
        animation: float 3s ease-in-out infinite;
    }
    
    .animate-glow {
        animation: glow 2s ease-in-out infinite;
    }
    
    /* ===== AUTO DEMO MODE ===== */
    @keyframes slideProgress {
        0% { width: 0%; }
        100% { width: 100%; }
    }
    
    @keyframes demoBannerPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.9; }
    }
    
    .demo-banner {
        animation: demoBannerPulse 2s ease-in-out infinite;
    }
    
    .demo-progress-bar {
        animation: slideProgress 7s linear;
    }
    
    @keyframes pageTransition {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .page-content {
        animation: pageTransition 0.5s ease-out;
    }
    
    /* VC Demo Caption Overlay */
    @keyframes captionSlideIn {
        0% { opacity: 0; transform: translateY(-20px); }
        15% { opacity: 1; transform: translateY(0); }
        85% { opacity: 1; transform: translateY(0); }
        100% { opacity: 0.9; transform: translateY(0); }
    }
    
    .vc-caption-overlay {
        animation: captionSlideIn 6.5s ease-out forwards;
    }
    
    /* File Drop Animation */
    @keyframes fileDrop {
        0% { opacity: 0; transform: translateY(-60px) scale(0.8); }
        40% { opacity: 1; transform: translateY(10px) scale(1.05); }
        60% { transform: translateY(-5px) scale(1); }
        80% { transform: translateY(3px) scale(1); }
        100% { transform: translateY(0) scale(1); }
    }
    
    @keyframes fileGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(255, 107, 53, 0.3); }
        50% { box-shadow: 0 0 40px rgba(255, 107, 53, 0.6), 0 0 60px rgba(255, 179, 71, 0.3); }
    }
    
    .file-drop-animation {
        animation: fileDrop 1.2s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
    }
    
    .file-glow {
        animation: fileGlow 2s ease-in-out infinite;
    }
    
    @keyframes processingPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    @keyframes progressScan {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .scanning-bar {
        position: relative;
        overflow: hidden;
    }
    
    .scanning-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,107,53,0.4), transparent);
        animation: progressScan 1.5s ease-in-out infinite;
    }
    
    /* ===== COUNTING NUMBER ANIMATION ===== */
    @keyframes countUp {
        0% { opacity: 0; transform: translateY(20px); }
        20% { opacity: 1; transform: translateY(0); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .count-up {
        animation: countUp 0.8s ease-out forwards;
    }
    
    .count-up-delay-1 { animation-delay: 0.1s; opacity: 0; }
    .count-up-delay-2 { animation-delay: 0.2s; opacity: 0; }
    .count-up-delay-3 { animation-delay: 0.3s; opacity: 0; }
    .count-up-delay-4 { animation-delay: 0.4s; opacity: 0; }
    
    /* ===== SUCCESS BURST ANIMATION ===== */
    @keyframes successBurst {
        0% { transform: scale(0.8); opacity: 0; }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes successGlow {
        0%, 100% { box-shadow: 0 0 0 rgba(0, 186, 124, 0); }
        50% { box-shadow: 0 0 20px rgba(0, 186, 124, 0.4), 0 0 40px rgba(0, 186, 124, 0.2); }
    }
    
    .success-burst {
        animation: successBurst 0.5s ease-out forwards, successGlow 2s ease-in-out infinite;
    }
    
    .success-check {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        background: linear-gradient(135deg, #00BA7C 0%, #34D399 100%);
        border-radius: 50%;
        color: white;
        font-size: 14px;
        animation: successBurst 0.4s ease-out forwards;
    }
    
    /* ===== PAGE FADE TRANSITION ===== */
    @keyframes pageFadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .page-fade-in {
        animation: pageFadeIn 0.4s ease-out forwards;
    }
    
    /* ===== IMPACT PAGE ANIMATIONS ===== */
    @keyframes impactNumber {
        0% { opacity: 0; transform: scale(0.5); }
        60% { transform: scale(1.1); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    .impact-number {
        animation: impactNumber 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
    }
    
    .impact-number-delay-1 { animation-delay: 0.15s; opacity: 0; }
    .impact-number-delay-2 { animation-delay: 0.3s; opacity: 0; }
    .impact-number-delay-3 { animation-delay: 0.45s; opacity: 0; }
    
    /* ===== ENTERPRISE BADGE ===== */
    .enterprise-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, rgba(255,107,53,0.1) 0%, rgba(255,179,71,0.05) 100%);
        border: 1px solid rgba(255,107,53,0.3);
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--forge-orange);
        letter-spacing: 0.03em;
    }
    
    /* ===== BEFORE/AFTER COMPARISON ===== */
    .comparison-card {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.25rem;
        position: relative;
        overflow: hidden;
    }
    
    .comparison-before {
        border-color: rgba(244, 33, 46, 0.2);
        background: linear-gradient(145deg, rgba(244, 33, 46, 0.03) 0%, transparent 100%);
    }
    
    .comparison-after {
        border-color: rgba(0, 186, 124, 0.3);
        background: linear-gradient(145deg, rgba(0, 186, 124, 0.05) 0%, transparent 100%);
    }
    
    .comparison-label {
        position: absolute;
        top: 0.75rem;
        right: 0.75rem;
        padding: 0.25rem 0.75rem;
        border-radius: 100px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .comparison-label-before {
        background: rgba(244, 33, 46, 0.15);
        color: var(--forge-error);
    }
    
    .comparison-label-after {
        background: rgba(0, 186, 124, 0.15);
        color: var(--forge-success);
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: var(--glass-bg) !important;
        border-radius: 12px !important;
        border: 1px solid var(--glass-border) !important;
    }
    
    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {
        background: transparent;
    }
    
    [data-testid="stFileUploader"] > div {
        background: rgba(15, 20, 25, 0.95) !important;
        border: 2px dashed rgba(255, 107, 53, 0.4);
        border-radius: 16px;
        padding: 2rem;
    }
    
    [data-testid="stFileUploader"] > div:hover {
        border-color: var(--forge-orange);
        background: rgba(255, 107, 53, 0.08) !important;
    }
    
    /* File uploader text styling - ensure visibility */
    [data-testid="stFileUploader"] section {
        background: transparent !important;
    }
    
    [data-testid="stFileUploader"] section > div {
        background: transparent !important;
    }
    
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] div {
        color: var(--forge-text) !important;
    }
    
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
        background: rgba(15, 20, 25, 0.95) !important;
    }
    
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] span {
        color: var(--forge-text) !important;
    }
    
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] div {
        color: var(--forge-text-muted) !important;
    }
    
    /* Browse files button */
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #FF6B35 0%, #FF8C42 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stFileUploader"] button:hover {
        background: linear-gradient(135deg, #FF8C42 0%, #FFB347 100%) !important;
    }
    
    /* ===== INPUT FIELDS ===== */
    .stTextInput > div > div {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
    }
    
    .stTextInput > div > div:focus-within {
        border-color: var(--forge-orange);
        box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.2);
    }
    
    .stSelectbox > div > div {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
    }
    
    /* ===== RADIO BUTTONS ===== */
    .stRadio > div {
        background: transparent;
    }
    
    .stRadio > div > label {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 0.875rem 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .stRadio > div > label:hover {
        border-color: rgba(255, 107, 53, 0.3);
    }
    
    /* ===== FEATURE GRID ===== */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.5rem;
        padding: 0.5rem;
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        border-radius: 8px;
        font-size: 0.8rem;
        color: var(--forge-text-muted);
    }
    
    .feature-item:hover {
        background: rgba(255, 255, 255, 0.03);
        color: var(--forge-text);
    }
    
    /* ===== RESPONSIVE UTILITIES ===== */
    .flex-row {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .flex-col {
        flex: 1;
        min-width: 200px;
    }
    
    /* ===== RESPONSIVE MEDIA QUERIES ===== */
    
    /* Large screens (default) */
    @media screen and (min-width: 1200px) {
        .hero-title { font-size: 3.5rem; }
        .metric-value { font-size: 2.75rem; }
        .glass-card { padding: 1.75rem; }
    }
    
    /* Medium screens - Tablets/Small laptops */
    @media screen and (max-width: 1199px) {
        .hero-title { font-size: 2.75rem; }
        .hero-subtitle { font-size: 1.1rem; }
        .metric-value { font-size: 2.25rem; }
        .metric-label { font-size: 0.75rem; }
        .glass-card { padding: 1.5rem; border-radius: 16px; }
        .glass-card-sm { padding: 0.875rem 1rem; }
        .process-step { padding: 1.25rem 0.875rem; }
        .section-title { font-size: 1.35rem; }
        .upload-zone { padding: 3rem 1.5rem; }
        .upload-icon { font-size: 3rem; }
        .upload-title { font-size: 1.25rem; }
        .feature-grid { gap: 0.375rem; }
    }
    
    /* Small screens - Mobile landscape */
    @media screen and (max-width: 900px) {
        .hero-title { font-size: 2.25rem; }
        .hero-subtitle { font-size: 1rem; }
        .metric-value { font-size: 2rem; }
        .metric-label { font-size: 0.7rem; letter-spacing: 0.05em; }
        .metric-card { padding: 1.25rem; border-radius: 12px; }
        .glass-card { padding: 1.25rem; border-radius: 14px; }
        .glass-card-sm { padding: 0.75rem 0.875rem; border-radius: 10px; }
        .section-title { font-size: 1.2rem; margin-bottom: 1rem; }
        .section-title::before { width: 3px; height: 20px; }
        .process-container { gap: 0.75rem; }
        .process-step { min-width: 120px; padding: 1rem 0.75rem; }
        .process-step::after { display: none; }
        .step-number { width: 28px; height: 28px; font-size: 0.8rem; }
        .step-icon { font-size: 1.75rem; }
        .step-title { font-size: 0.85rem; }
        .step-desc { font-size: 0.7rem; }
        .upload-zone { padding: 2.5rem 1rem; border-radius: 18px; }
        .upload-icon { font-size: 2.5rem; margin-bottom: 1rem; }
        .upload-title { font-size: 1.15rem; }
        .upload-subtitle { font-size: 0.8rem; }
        .badge { padding: 0.4rem 0.8rem; font-size: 0.7rem; }
        .pill { padding: 0.3rem 0.7rem; font-size: 0.7rem; }
        .feature-grid { grid-template-columns: 1fr 1fr; }
        .nav-item { padding: 0.75rem 0.875rem; font-size: 0.85rem; }
    }
    
    /* Extra small screens - Mobile portrait */
    @media screen and (max-width: 600px) {
        .hero-title { font-size: 1.75rem; line-height: 1.2; }
        .hero-subtitle { font-size: 0.9rem; margin-top: 0.5rem; }
        .metric-value { font-size: 1.75rem; }
        .metric-label { font-size: 0.65rem; }
        .metric-card { padding: 1rem; border-radius: 10px; }
        .glass-card { padding: 1rem; border-radius: 12px; }
        .glass-card-sm { padding: 0.65rem 0.75rem; border-radius: 8px; }
        .section-title { font-size: 1.1rem; gap: 0.5rem; }
        .section-title::before { width: 3px; height: 18px; }
        .process-container { flex-direction: column; }
        .process-step { min-width: 100%; padding: 1rem; }
        .upload-zone { padding: 2rem 1rem; border-radius: 14px; }
        .upload-icon { font-size: 2rem; margin-bottom: 0.75rem; }
        .upload-title { font-size: 1rem; }
        .badge { padding: 0.35rem 0.65rem; font-size: 0.65rem; gap: 0.35rem; }
        .pill { padding: 0.25rem 0.6rem; font-size: 0.65rem; margin: 0.15rem; }
        .feature-grid { grid-template-columns: 1fr; gap: 0.25rem; }
        .feature-item { font-size: 0.75rem; padding: 0.4rem; }
        .sidebar-brand { font-size: 1.5rem; }
        .sidebar-tagline { font-size: 0.65rem; }
        .nav-item { padding: 0.65rem 0.75rem; font-size: 0.8rem; gap: 0.5rem; }
        .nav-icon { font-size: 1rem; width: 20px; }
    }
    
    /* Streamlit specific responsive overrides */
    @media screen and (max-width: 900px) {
        [data-testid="stVerticalBlock"] > div { gap: 0.75rem !important; }
        [data-testid="column"] { min-width: 0 !important; }
        [data-testid="stFileUploader"] > div { padding: 1.5rem; }
    }
    
    @media screen and (max-width: 600px) {
        [data-testid="stVerticalBlock"] > div { gap: 0.5rem !important; }
        [data-testid="stFileUploader"] > div { padding: 1rem; border-radius: 12px; }
        .stButton > button { padding: 0.6rem 1rem; font-size: 0.85rem; border-radius: 10px; }
    }
    
    /* Fix Streamlit columns on small screens */
    @media screen and (max-width: 768px) {
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 45% !important;
            min-width: 45% !important;
        }
    }
    
    /* Override for metric cards to stack on small screens */
    @media screen and (max-width: 480px) {
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
    }
    
    /* ===== RESPONSIVE TEXT UTILITIES ===== */
    .resp-text-xl {
        font-size: clamp(1.5rem, 4vw, 2.75rem);
    }
    
    .resp-text-lg {
        font-size: clamp(1.25rem, 3vw, 2rem);
    }
    
    .resp-text-md {
        font-size: clamp(0.9rem, 2vw, 1.25rem);
    }
    
    .resp-text-sm {
        font-size: clamp(0.7rem, 1.5vw, 0.85rem);
    }
    
    /* Responsive card grid */
    .responsive-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
    }
    
    /* Text truncation for long strings */
    .truncate {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
    }
    
    /* Responsive flex container */
    .flex-responsive {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        align-items: center;
    }
    
    /* Make charts responsive */
    .chart-container {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    /* Min-width for inline items */
    .glass-card-sm {
        min-width: 0;
        overflow: hidden;
    }
    
    .glass-card {
        min-width: 0;
        overflow: hidden;
    }
    
    /* Word break for long content */
    .glass-card *, .glass-card-sm * {
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    /* Job card flex fixes */
    @media screen and (max-width: 600px) {
        .glass-card-sm > div {
            flex-wrap: wrap !important;
            gap: 0.5rem !important;
        }
        
        .glass-card-sm .badge {
            font-size: 0.6rem !important;
            padding: 0.2rem 0.4rem !important;
        }
        
        .glass-card-sm code {
            font-size: 0.6rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# ===== API Functions =====
def get_api_health():
    try:
        response = requests.get(f"{API_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False


def upload_installer(file):
    try:
        files = {"file": (file.name, file.getvalue(), "application/octet-stream")}
        response = requests.post(f"{API_URL}/packages/upload", files=files)
        if response.status_code == 200:
            return response.json()
        st.error(f"Upload failed: {response.text}")
        return None
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def get_job_status(job_id):
    try:
        response = requests.get(f"{API_URL}/packages/{job_id}")
        return response.json() if response.status_code == 200 else None
    except:
        return None


def get_all_jobs():
    try:
        response = requests.get(f"{API_URL}/packages")
        return response.json() if response.status_code == 200 else []
    except:
        return []


def get_knowledge_stats():
    try:
        response = requests.get(f"{API_URL}/knowledge/stats")
        return response.json() if response.status_code == 200 else {}
    except:
        return {}


def search_knowledge(query):
    try:
        response = requests.get(f"{API_URL}/knowledge/search", params={"query": query})
        return response.json() if response.status_code == 200 else {"results": []}
    except:
        return {"results": []}


# ===== Sidebar =====
def render_sidebar():
    with st.sidebar:
        # Corporate Logo & Brand
        st.markdown("""
        <div class="sidebar-logo">
            <div class="forge-logo-mark">
                <svg width="56" height="56" viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <!-- Shield base -->
                    <path d="M28 4L6 14V28C6 40.36 15.48 51.68 28 54C40.52 51.68 50 40.36 50 28V14L28 4Z" 
                          fill="url(#shield_gradient)" stroke="url(#shield_stroke)" stroke-width="1.5"/>
                    <!-- Inner forge flame/anvil mark -->
                    <path d="M28 14L20 22V32L28 40L36 32V22L28 14Z" fill="url(#inner_gradient)" opacity="0.9"/>
                    <path d="M28 18L23 24V30L28 36L33 30V24L28 18Z" fill="#0F1419"/>
                    <path d="M28 22L25 26V29L28 33L31 29V26L28 22Z" fill="url(#core_gradient)"/>
                    <!-- Accent lines -->
                    <path d="M14 20L18 24" stroke="url(#accent_gradient)" stroke-width="2" stroke-linecap="round"/>
                    <path d="M42 20L38 24" stroke="url(#accent_gradient)" stroke-width="2" stroke-linecap="round"/>
                    <path d="M14 36L18 32" stroke="url(#accent_gradient)" stroke-width="2" stroke-linecap="round"/>
                    <path d="M42 36L38 32" stroke="url(#accent_gradient)" stroke-width="2" stroke-linecap="round"/>
                    <defs>
                        <linearGradient id="shield_gradient" x1="28" y1="4" x2="28" y2="54" gradientUnits="userSpaceOnUse">
                            <stop offset="0%" stop-color="#1A1F26"/>
                            <stop offset="100%" stop-color="#0D1117"/>
                        </linearGradient>
                        <linearGradient id="shield_stroke" x1="6" y1="14" x2="50" y2="54" gradientUnits="userSpaceOnUse">
                            <stop offset="0%" stop-color="#FF6B35"/>
                            <stop offset="50%" stop-color="#FFB347"/>
                            <stop offset="100%" stop-color="#FF6B35"/>
                        </linearGradient>
                        <linearGradient id="inner_gradient" x1="28" y1="14" x2="28" y2="40" gradientUnits="userSpaceOnUse">
                            <stop offset="0%" stop-color="#FF6B35"/>
                            <stop offset="100%" stop-color="#FF8C5A"/>
                        </linearGradient>
                        <linearGradient id="core_gradient" x1="28" y1="22" x2="28" y2="33" gradientUnits="userSpaceOnUse">
                            <stop offset="0%" stop-color="#FFB347"/>
                            <stop offset="100%" stop-color="#FF6B35"/>
                        </linearGradient>
                        <linearGradient id="accent_gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#FF6B35" stop-opacity="0.6"/>
                            <stop offset="100%" stop-color="#FFB347" stop-opacity="0.3"/>
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            <div class="sidebar-brand">FORGE</div>
            <div class="sidebar-tagline">Enterprise Endpoint Compliance</div>
            <div class="sidebar-tagline-sub">AI-Powered Automation Platform</div>
        </div>
        """, unsafe_allow_html=True)
        
        # API Status
        api_ok = get_api_health()
        status_class = "online" if api_ok else "offline"
        status_text = "Connected" if api_ok else "Offline"
        text_color = "var(--forge-text)" if api_ok else "var(--forge-text-muted)"
        st.markdown(f"""
        <div class="sidebar-section">
            <div class="glass-card-sm" style="display: flex; align-items: center; gap: 0.75rem;">
                <span class="status-dot status-dot-{status_class}"></span>
                <span style="font-size: 0.85rem; color: {text_color};">
                    API {status_text}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
        
        # Initialize session state for demo - restore from query params if page was reloaded
        query_params = st.query_params
        if 'auto_demo' not in st.session_state:
            # Check if demo was active before reload (via query param)
            st.session_state.auto_demo = query_params.get('demo', '') == '1'
        if 'demo_page_index' not in st.session_state:
            st.session_state.demo_page_index = int(query_params.get('idx', '0'))
        if 'demo_start_time' not in st.session_state:
            # Restore start time from query params, or use current time
            saved_time = query_params.get('t', '')
            if saved_time:
                st.session_state.demo_start_time = float(saved_time)
            else:
                st.session_state.demo_start_time = time.time()
        
        # Navigation - index synced with demo mode
        st.markdown('<div class="sidebar-section-title">Navigation</div>', unsafe_allow_html=True)
        
        # Determine the current page index - must match AUTO_DEMO_PAGES
        nav_options = ["🏠  Upload", "📦  Jobs", "📊  Dashboard", "🔍  Search"]
        if st.session_state.auto_demo:
            current_index = st.session_state.demo_page_index % len(nav_options)
        else:
            current_index = 0
        
        page = st.radio(
            "nav",
            nav_options,
            index=current_index,
            label_visibility="collapsed",
            key="nav_radio",
            disabled=st.session_state.auto_demo  # Disable during auto-demo
        )
        
        # Only show sidebar content when NOT in demo mode
        if not st.session_state.auto_demo:
            st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
            
            # Quick Stats
            st.markdown('<div class="sidebar-section-title">Knowledge Base</div>', unsafe_allow_html=True)
            stats = MOCK_STATS if DEMO_MODE else get_knowledge_stats()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="metric-card" style="--metric-color: var(--forge-orange);">
                    <div class="metric-value" style="color: var(--forge-orange);">{stats.get('total_packages', 247)}</div>
                    <div class="metric-label">Apps</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card" style="--metric-color: var(--forge-info);">
                    <div class="metric-value" style="color: var(--forge-info);">{stats.get('total_commands', 1892)}</div>
                <div class="metric-label">Commands</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
            
            # Features
            st.markdown('<div class="sidebar-section-title">Capabilities</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="feature-grid">
                <div class="feature-item">🤖 AI Analysis</div>
                <div class="feature-item">🛡️ WDAC Policy</div>
                <div class="feature-item">📦 Auto Package</div>
                <div class="feature-item">🔍 RAG Search</div>
                <div class="feature-item">⚡ Fast Deploy</div>
                <div class="feature-item">✅ Compliance</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
        
        # Auto Demo Mode Toggle
        st.markdown('<div class="sidebar-section-title">Demo Mode</div>', unsafe_allow_html=True)
        
        auto_demo = st.toggle("🎬 Auto Demo", value=st.session_state.auto_demo, help="Auto-cycle through pages every 4 seconds")
        
        if auto_demo != st.session_state.auto_demo:
            st.session_state.auto_demo = auto_demo
            st.session_state.demo_start_time = time.time()
            st.session_state.demo_page_index = 0
            # Set/clear query params to persist across page refresh
            if auto_demo:
                st.query_params['demo'] = '1'
                st.query_params['idx'] = '0'
                st.query_params['t'] = str(time.time())
            else:
                st.query_params.clear()
            st.rerun()
        
        if st.session_state.auto_demo:
            # Calculate time remaining using per-page timing
            current_page_name = AUTO_DEMO_PAGES[st.session_state.demo_page_index % len(AUTO_DEMO_PAGES)]
            page_interval = AUTO_DEMO_PAGE_TIMES.get(current_page_name, AUTO_DEMO_INTERVAL)
            elapsed = time.time() - st.session_state.demo_start_time
            remaining = max(0, page_interval - elapsed)
            progress = min(1.0, elapsed / page_interval)
            remaining_display = max(1, math.ceil(remaining)) if remaining > 0.1 else 0  # Proper countdown
            
            next_page_name = AUTO_DEMO_PAGES[(st.session_state.demo_page_index + 1) % len(AUTO_DEMO_PAGES)]
            
            # Create a live countdown display
            st.markdown(f'<div class="glass-card-sm" style="margin-top: 0.5rem;"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;"><span style="font-size: 0.75rem; color: var(--forge-text-muted);">Next: {next_page_name}</span><span style="font-size: 1.25rem; font-weight: 800; color: var(--forge-orange);">{remaining_display}</span></div><div style="height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;"><div style="height: 100%; width: {progress*100:.0f}%; background: linear-gradient(90deg, var(--forge-orange), var(--forge-gold)); border-radius: 3px; transition: width 0.3s ease;"></div></div></div>', unsafe_allow_html=True)
            
            # Return the demo page, overriding the radio selection
            page = current_page_name
        
        return page


# ===== Upload Page =====
def render_upload_page():
    is_auto_demo = st.session_state.get('auto_demo', False)
    
    # Auto-scroll animation for demo mode - scroll 1000px in 1.5 seconds to reach upload section
    if is_auto_demo:
        demo_elapsed = time.time() - st.session_state.get('demo_start_time', time.time())
        # Scroll down in first 1.5 seconds, then maintain position
        if demo_elapsed < 1.5:
            scroll_progress = min(1.0, demo_elapsed / 1.5)  # 0 to 1 over 1.5 seconds
            scroll_target = int(scroll_progress * 1000)  # Scroll up to 1000px
            components.html(f'''<script>window.parent.document.querySelector('[data-testid="stAppViewContainer"]').scrollTo({{top: {scroll_target}, behavior: 'smooth'}});</script>''', height=0)
        else:
            # Keep scroll position at 1000px after initial scroll
            components.html('''<script>window.parent.document.querySelector('[data-testid="stAppViewContainer"]').scrollTo({top: 1000, behavior: 'auto'});</script>''', height=0)
    
    # Corporate Hero Section with inline SVG logo
    st.markdown("""
    <div style="text-align: center; padding: clamp(1.5rem, 4vw, 3rem) 0 clamp(1rem, 2vw, 1.5rem);">
        <div class="hero-logo-container">
            <svg width="72" height="72" viewBox="0 0 56 56" fill="none" xmlns="http://www.w3.org/2000/svg" class="hero-logo">
                <path d="M28 4L6 14V28C6 40.36 15.48 51.68 28 54C40.52 51.68 50 40.36 50 28V14L28 4Z" 
                      fill="url(#hero_shield)" stroke="url(#hero_stroke)" stroke-width="1.5"/>
                <path d="M28 14L20 22V32L28 40L36 32V22L28 14Z" fill="url(#hero_inner)" opacity="0.9"/>
                <path d="M28 18L23 24V30L28 36L33 30V24L28 18Z" fill="#0F1419"/>
                <path d="M28 22L25 26V29L28 33L31 29V26L28 22Z" fill="url(#hero_core)"/>
                <defs>
                    <linearGradient id="hero_shield" x1="28" y1="4" x2="28" y2="54" gradientUnits="userSpaceOnUse">
                        <stop offset="0%" stop-color="#1A1F26"/>
                        <stop offset="100%" stop-color="#0D1117"/>
                    </linearGradient>
                    <linearGradient id="hero_stroke" x1="6" y1="14" x2="50" y2="54" gradientUnits="userSpaceOnUse">
                        <stop offset="0%" stop-color="#FF6B35"/>
                        <stop offset="50%" stop-color="#FFB347"/>
                        <stop offset="100%" stop-color="#FF6B35"/>
                    </linearGradient>
                    <linearGradient id="hero_inner" x1="28" y1="14" x2="28" y2="40" gradientUnits="userSpaceOnUse">
                        <stop offset="0%" stop-color="#FF6B35"/>
                        <stop offset="100%" stop-color="#FF8C5A"/>
                    </linearGradient>
                    <linearGradient id="hero_core" x1="28" y1="22" x2="28" y2="33" gradientUnits="userSpaceOnUse">
                        <stop offset="0%" stop-color="#FFB347"/>
                        <stop offset="100%" stop-color="#FF6B35"/>
                    </linearGradient>
                </defs>
            </svg>
        </div>
        <h1 class="hero-title">FORGE</h1>
        <p class="hero-subtitle">Enterprise-grade installer packaging with AI-powered compliance automation</p>
        <div class="hero-badges">
            <span class="hero-badge">🛡️ WDAC Ready</span>
            <span class="hero-badge">🤖 AI-Powered</span>
            <span class="hero-badge">⚡ Zero-Touch</span>
        </div>
        <div style="margin-top: 1.25rem; display: flex; justify-content: center; gap: 0.75rem; flex-wrap: wrap;">
            <span class="enterprise-badge">🏢 Enterprise Ready</span>
            <span class="enterprise-badge">🔒 SOC 2 Compliant</span>
            <span class="enterprise-badge">🌐 Azure Integrated</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Process Steps
    st.markdown("""
    <div class="process-container">
        <div class="process-step" style="--step-color: #FF6B35; --step-color-end: #FF8C5A;">
            <div class="step-number">1</div>
            <div class="step-icon">📤</div>
            <div class="step-title">Upload</div>
            <div class="step-desc">Drop your installer</div>
        </div>
        <div class="process-step" style="--step-color: #3B82F6; --step-color-end: #60A5FA;">
            <div class="step-number">2</div>
            <div class="step-icon">🤖</div>
            <div class="step-title">Analyze</div>
            <div class="step-desc">AI discovers switches</div>
        </div>
        <div class="process-step" style="--step-color: #8B5CF6; --step-color-end: #A78BFA;">
            <div class="step-number">3</div>
            <div class="step-icon">📦</div>
            <div class="step-title">Package</div>
            <div class="step-desc">Generate scripts</div>
        </div>
        <div class="process-step" style="--step-color: #10B981; --step-color-end: #34D399;">
            <div class="step-number">4</div>
            <div class="step-icon">🛡️</div>
            <div class="step-title">Secure</div>
            <div class="step-desc">WDAC policy ready</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
    
    is_auto_demo = st.session_state.get('auto_demo', False)
    
    # Upload Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-title">Upload Installer</div>', unsafe_allow_html=True)
        
        if is_auto_demo:
            # Animated file drop simulation for VC demo
            demo_elapsed = time.time() - st.session_state.get('demo_start_time', time.time())
            
            if demo_elapsed < 4:
                # Phase 1: Show upload zone with file dropping in (0-4 seconds)
                st.markdown('''
                <div class="upload-zone" style="position: relative; overflow: visible;">
                    <div class="file-drop-animation" style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); z-index: 10;">
                        <div class="file-glow" style="background: linear-gradient(145deg, rgba(255,107,53,0.15) 0%, rgba(255,179,71,0.1) 100%); border: 2px solid rgba(255,107,53,0.5); border-radius: 12px; padding: 1rem 1.5rem; display: flex; align-items: center; gap: 0.75rem;">
                            <span style="font-size: 2rem;">📁</span>
                            <div>
                                <div style="font-weight: 700; color: var(--forge-text); font-size: 0.95rem;">Chrome_Enterprise.msi</div>
                                <div style="font-size: 0.75rem; color: var(--forge-text-muted);">84.2 MB</div>
                            </div>
                        </div>
                    </div>
                    <div style="padding-top: 4rem;">
                        <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;">📤</div>
                        <div class="upload-title" style="opacity: 0.7;">Drop your installer here</div>
                        <div class="upload-subtitle">Supports MSI, EXE, MSIX formats</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            else:
                # Phase 2: Show "analyzing" state with progress (4-10 seconds, 0% to 80%)
                analysis_progress = min(80, int((demo_elapsed - 4) / 6 * 80))
                st.markdown(f'<div class="glass-card" style="border-color: rgba(255,107,53,0.4); position: relative; overflow: hidden;"><div style="display: flex; align-items: center; gap: 1.25rem; flex-wrap: wrap;"><div style="font-size: 3rem;">📁</div><div style="flex: 1; min-width: 200px;"><div style="font-weight: 700; font-size: 1.1rem; color: var(--forge-text); margin-bottom: 0.25rem;">Chrome_Enterprise.msi</div><div style="font-size: 0.85rem; color: var(--forge-text-muted); margin-bottom: 0.75rem;">84.2 MB • Google LLC</div><div style="display: flex; align-items: center; gap: 0.75rem;"><div class="scanning-bar" style="flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px;"><div style="height: 100%; width: {analysis_progress}%; background: linear-gradient(90deg, #FF6B35, #FFB347); border-radius: 3px; transition: width 0.3s ease;"></div></div><span style="font-size: 0.8rem; font-weight: 600; color: var(--forge-orange);">{analysis_progress}%</span></div></div><div class="badge badge-processing" style="animation: processingPulse 1.5s infinite;">🤖 AI Analyzing</div></div><div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); display: flex; gap: 1.5rem; flex-wrap: wrap;"><div style="font-size: 0.8rem;"><span style="color: var(--forge-text-muted);">Detected:</span> <span style="color: var(--forge-success); font-weight: 600;">MSI Installer</span></div><div style="font-size: 0.8rem;"><span style="color: var(--forge-text-muted);">Switches:</span> <span class="pill" style="margin: 0;">/qn</span> <span class="pill" style="margin: 0;">/norestart</span></div></div></div>', unsafe_allow_html=True)
        else:
            uploaded_file = st.file_uploader(
                "Drag and drop your installer here",
                type=["msi", "exe", "msix"],
                help="Supported: MSI, EXE, MSIX",
                label_visibility="collapsed",
                key="file_uploader"
            )
            
            if uploaded_file:
                file_size = uploaded_file.size / 1024
                size_unit = "KB" if file_size < 1024 else "MB"
                size_val = file_size if file_size < 1024 else file_size / 1024
                
                st.markdown(f"""
                <div class="glass-card" style="margin: 1.5rem 0;">
                    <div style="display: flex; align-items: center; gap: clamp(0.75rem, 2vw, 1.25rem); flex-wrap: wrap;">
                        <div style="font-size: clamp(2rem, 5vw, 3rem); opacity: 0.9;">📁</div>
                        <div style="flex: 1; min-width: 150px;">
                            <div style="font-weight: 600; font-size: clamp(0.9rem, 2vw, 1.1rem); color: var(--forge-text); margin-bottom: 0.25rem; word-break: break-all;">
                                {uploaded_file.name}
                            </div>
                            <div style="font-size: clamp(0.75rem, 1.5vw, 0.85rem); color: var(--forge-text-muted);">
                                {size_val:.1f} {size_unit} • Ready to process
                            </div>
                        </div>
                        <span class="badge badge-success">Ready</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🚀 Start Packaging", type="primary", use_container_width=True, key="start_packaging"):
                    with st.spinner("Uploading and analyzing..."):
                        result = upload_installer(uploaded_file)
                        if result:
                            st.session_state.current_job_id = result["id"]
                            st.success(f"✅ Job created: **{result['id']}**")
                            time.sleep(1)
                            st.rerun()
    
    with col2:
        st.markdown('<div class="section-title">Quick Stats</div>', unsafe_allow_html=True)
        
        jobs = MOCK_JOBS if DEMO_MODE else get_all_jobs()
        completed = len([j for j in jobs if j["status"] == "completed"])
        pending = len([j for j in jobs if j["status"] in ["pending", "analyzing", "packaging"]])
        needs_review = len([j for j in jobs if j["status"] == "needs_review"])
        
        # Get knowledge base stats
        stats = MOCK_STATS if DEMO_MODE else get_knowledge_stats()
        
        if is_auto_demo:
            # During demo mode, show knowledge base stats prominently
            st.markdown(f'''
            <div class="glass-card" style="margin-bottom: 1rem; border-color: rgba(255,107,53,0.3);">
                <div style="font-size: 0.7rem; color: var(--forge-text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">Knowledge Base</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 1.75rem; font-weight: 800; color: var(--forge-orange);">{stats.get('total_packages', 247)}</div>
                        <div style="font-size: 0.75rem; color: var(--forge-text-muted);">Apps</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.75rem; font-weight: 800; color: var(--forge-info);">{stats.get('total_commands', 1892)}</div>
                        <div style="font-size: 0.75rem; color: var(--forge-text-muted);">Commands</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="glass-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                <span style="color: var(--forge-text-muted); font-size: clamp(0.8rem, 2vw, 1rem);">✅ Completed</span>
                <span style="font-size: clamp(1.25rem, 4vw, 1.75rem); font-weight: 700; color: var(--forge-success);">{completed}</span>
            </div>
        </div>
        <div class="glass-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                <span style="color: var(--forge-text-muted); font-size: clamp(0.8rem, 2vw, 1rem;">⏳ In Progress</span>
                <span style="font-size: clamp(1.25rem, 4vw, 1.75rem); font-weight: 700; color: var(--forge-info);">{pending}</span>
            </div>
        </div>
        <div class="glass-card" style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                <span style="color: var(--forge-text-muted); font-size: clamp(0.8rem, 2vw, 1rem);">⚠️ Needs Review</span>
                <span style="font-size: clamp(1.25rem, 4vw, 1.75rem); font-weight: 700; color: var(--forge-warning);">{needs_review}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Current Job Status - skip during auto-demo to avoid widget conflicts
    if not is_auto_demo and "current_job_id" in st.session_state:
        render_job_details(st.session_state.current_job_id)
    
    # Before/After ROI Comparison - only show when NOT in auto-demo
    if not is_auto_demo:
        st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">The Forge Difference</div>', unsafe_allow_html=True)
        
        col_before, col_after = st.columns(2)
        
        with col_before:
            st.markdown('''
            <div class="comparison-card comparison-before">
                <span class="comparison-label comparison-label-before">❌ Before</span>
                <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">😩</div>
                <div style="font-size: 1.5rem; font-weight: 800; color: var(--forge-error); margin-bottom: 0.5rem;">4-6 Hours</div>
                <div style="font-size: 0.85rem; color: var(--forge-text-muted); margin-bottom: 1rem;">Per application package</div>
                <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem; font-size: 0.8rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; color: var(--forge-text-muted);">
                        <span style="color: var(--forge-error);">✗</span> Manual switch discovery
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; color: var(--forge-text-muted);">
                        <span style="color: var(--forge-error);">✗</span> Trial and error testing
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; color: var(--forge-text-muted);">
                        <span style="color: var(--forge-error);">✗</span> Policy creation from scratch
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col_after:
            st.markdown('''
            <div class="comparison-card comparison-after">
                <span class="comparison-label comparison-label-after">✔ With Forge</span>
                <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🚀</div>
                <div style="font-size: 1.5rem; font-weight: 800; color: var(--forge-success); margin-bottom: 0.5rem;">2.3 Minutes</div>
                <div style="font-size: 0.85rem; color: var(--forge-text-muted); margin-bottom: 1rem;">Fully automated end-to-end</div>
                <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem; font-size: 0.8rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; color: var(--forge-text);">
                        <span class="success-check">✓</span> AI-powered analysis
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; color: var(--forge-text);">
                        <span class="success-check">✓</span> 94% first-time accuracy
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; color: var(--forge-text);">
                        <span class="success-check">✓</span> WDAC policy auto-generated
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)


# ===== Job Details =====
def render_job_details(job_id):
    st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
    
    # Try mock data first in demo mode
    job = None
    if DEMO_MODE:
        job = next((j for j in MOCK_JOBS if j["id"] == job_id), None)
    if not job:
        job = get_job_status(job_id)
    if not job:
        st.error("Job not found")
        return
    
    # Status mapping
    status_config = {
        "completed": ("✅", "badge-success", "Completed"),
        "analyzing": ("🔍", "badge-processing", "Analyzing"),
        "packaging": ("📦", "badge-processing", "Packaging"),
        "validating": ("🛡️", "badge-processing", "Validating"),
        "pending": ("⏳", "badge-info", "Pending"),
        "failed": ("❌", "badge-error", "Failed"),
        "needs_review": ("⚠️", "badge-warning", "Needs Review"),
    }
    
    icon, badge_class, status_label = status_config.get(job["status"], ("⏳", "badge-info", "Unknown"))
    
    # Job Header
    st.markdown(f"""
    <div class="glass-card" style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
            <div>
                <div style="font-size: 0.7rem; color: var(--forge-text-muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem;">
                    Job ID
                </div>
                <div style="font-size: 1.25rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: var(--forge-text);">
                    {job_id}
                </div>
                <div style="color: var(--forge-text-muted); margin-top: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                    📁 {job['filename']}
                </div>
            </div>
            <span class="badge {badge_class}">{icon} {status_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh
    if job["status"] in ["pending", "analyzing", "packaging", "validating"]:
        time.sleep(2)
        st.rerun()
    
    # Results
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-title">Metadata</div>', unsafe_allow_html=True)
        if job.get("metadata"):
            meta = job["metadata"]
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: grid; gap: 1rem;">
                    <div style="display: flex; justify-content: space-between; padding-bottom: 0.75rem; border-bottom: 1px solid var(--glass-border);">
                        <span style="color: var(--forge-text-muted);">Product</span>
                        <span style="font-weight: 600;">{meta.get("product_name", "Unknown")}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding-bottom: 0.75rem; border-bottom: 1px solid var(--glass-border);">
                        <span style="color: var(--forge-text-muted);">Version</span>
                        <span style="font-weight: 600;">{meta.get("product_version", "Unknown")}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding-bottom: 0.75rem; border-bottom: 1px solid var(--glass-border);">
                        <span style="color: var(--forge-text-muted);">Manufacturer</span>
                        <span style="font-weight: 600;">{meta.get("manufacturer", "Unknown")}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--forge-text-muted);">Type</span>
                        <span class="pill">{meta.get("installer_type", "Unknown").upper()}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Extracting metadata...")
    
    with col2:
        st.markdown('<div class="section-title">AI Analysis</div>', unsafe_allow_html=True)
        if job.get("analysis"):
            analysis = job["analysis"]
            confidence = analysis.get("confidence", 0)
            
            if confidence >= 0.8:
                conf_color = "var(--forge-success)"
                conf_label = "High"
            elif confidence >= 0.6:
                conf_color = "var(--forge-warning)"
                conf_label = "Medium"
            else:
                conf_color = "var(--forge-error)"
                conf_label = "Low"
            
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; gap: 1.25rem; align-items: flex-start;">
                    <div style="text-align: center; min-width: 80px;">
                        <div style="font-size: 2rem; font-weight: 800; color: {conf_color};">{confidence:.0%}</div>
                        <div style="font-size: 0.7rem; color: var(--forge-text-muted); text-transform: uppercase;">{conf_label}</div>
                        <div class="confidence-bar" style="margin-top: 0.5rem;">
                            <div class="confidence-fill" style="width: {confidence*100}%; background: {conf_color};"></div>
                        </div>
                    </div>
                    <div style="flex: 1; font-size: 0.85rem; color: var(--forge-text-muted); line-height: 1.5;">
                        {analysis.get('reasoning', 'Analysis complete.')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("AI analysis in progress...")
    
    # Install Command
    if job.get("analysis") and job["analysis"].get("install_command"):
        st.markdown('<div class="section-title">Install Command</div>', unsafe_allow_html=True)
        st.code(job["analysis"]["install_command"], language="powershell")
        
        switches = job["analysis"].get("silent_switches", [])
        if switches:
            pills = "".join([f'<span class="pill">{s}</span>' for s in switches])
            st.markdown(f"<div style='margin-top: 0.5rem;'><strong style='color: var(--forge-text-muted);'>Switches:</strong> {pills}</div>", unsafe_allow_html=True)
    
    # WDAC Policy
    if job.get("policy"):
        st.markdown('<div class="section-title">WDAC Policy</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="glass-card" style="background: linear-gradient(145deg, rgba(16, 185, 129, 0.05) 0%, rgba(52, 211, 153, 0.02) 100%); border-color: rgba(16, 185, 129, 0.2);">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 2.5rem;">🛡️</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: var(--forge-success);">{job["policy"].get("policy_name", "WDAC Policy")}</div>
                    <div style="font-size: 0.85rem; color: var(--forge-text-muted);">Hash-based allowlist rule generated</div>
                </div>
                <span class="badge badge-success">Ready</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.checkbox("📄 Show Policy XML", key=f"policy_xml_{job_id}"):
            st.code(job["policy"].get("policy_xml", ""), language="xml")
    
    # Known Issues
    if job.get("analysis") and job["analysis"].get("known_issues"):
        st.markdown('<div class="section-title">Known Issues</div>', unsafe_allow_html=True)
        for issue in job["analysis"]["known_issues"]:
            st.warning(issue)
    
    # Error
    if job.get("error_message"):
        st.error(f"**Error:** {job['error_message']}")


# ===== Jobs Page =====
def render_jobs_page():
    is_auto_demo = st.session_state.get('auto_demo', False)
    
    # Auto-scroll for demo mode - scroll 400px in 1.5 seconds then hold
    if is_auto_demo:
        demo_elapsed = time.time() - st.session_state.get('demo_start_time', time.time())
        if demo_elapsed < 1.5:
            scroll_progress = min(1.0, demo_elapsed / 1.5)
            scroll_target = int(scroll_progress * 400)
            components.html(f'''<script>window.parent.document.querySelector('[data-testid="stAppViewContainer"]').scrollTo({{top: {scroll_target}, behavior: 'smooth'}});</script>''', height=0)
        else:
            components.html('''<script>window.parent.document.querySelector('[data-testid="stAppViewContainer"]').scrollTo({top: 400, behavior: 'auto'});</script>''', height=0)
    
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 class="hero-title" style="font-size: 2.5rem;">All Jobs</h1>
        <p class="hero-subtitle">Track and manage your packaging operations</p>
    </div>
    """, unsafe_allow_html=True)
    
    jobs = MOCK_JOBS if DEMO_MODE else get_all_jobs()
    
    if not jobs:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1.5rem; opacity: 0.5;">📦</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: var(--forge-text); margin-bottom: 0.5rem;">No jobs yet</div>
            <div style="color: var(--forge-text-muted);">Upload an installer to get started!</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Filters - disabled during auto-demo
    
    if not is_auto_demo:
        col1, col2, col3 = st.columns([2, 2, 6])
        with col1:
            status_filter = st.selectbox("Filter", ["All", "completed", "analyzing", "pending", "failed", "needs_review"], key="jobs_filter")
        with col2:
            sort_order = st.selectbox("Sort", ["Newest", "Oldest"], key="jobs_sort")
        
        if status_filter != "All":
            jobs = [j for j in jobs if j["status"] == status_filter]
        if sort_order == "Oldest":
            jobs = list(reversed(jobs))
    
    st.markdown(f"<div style='margin: 1rem 0; color: var(--forge-text-muted);'><strong>{len(jobs)}</strong> job(s)</div>", unsafe_allow_html=True)
    
    # Job Cards - show as static list during auto-demo
    # In demo mode, expand Chrome job after 3 seconds (simulating click)
    demo_elapsed = time.time() - st.session_state.get('demo_start_time', time.time()) if is_auto_demo else 0
    should_expand_chrome = is_auto_demo and demo_elapsed >= 3
    
    for idx, job in enumerate(jobs):
        icon_map = {"completed": "✅", "analyzing": "🔍", "packaging": "📦", "pending": "⏳", "failed": "❌", "needs_review": "⚠️"}
        icon = icon_map.get(job["status"], "⏳")
        badge_class = {"completed": "badge-success", "analyzing": "badge-processing", "pending": "badge-info", "failed": "badge-error", "needs_review": "badge-warning", "packaging": "badge-processing"}.get(job['status'], 'badge-info')
        
        # Add success burst animation for completed jobs during auto-demo
        is_completed = job["status"] == "completed"
        success_class = "success-burst" if is_completed and is_auto_demo else ""
        success_glow = "border-color: rgba(0,186,124,0.4); box-shadow: 0 0 20px rgba(0,186,124,0.15);" if is_completed and is_auto_demo else ""
        animation_delay = f"animation-delay: {idx * 0.1}s;" if is_auto_demo else ""
        
        if is_auto_demo:
            # Enhanced display during auto-demo with success animations
            confidence_html = ""
            if is_completed and job.get("analysis"):
                conf = job["analysis"].get("confidence", 0)
                conf_color = "var(--forge-success)" if conf >= 0.8 else "var(--forge-warning)"
                confidence_html = f'<span style="font-size: 0.8rem; font-weight: 700; color: {conf_color}; margin-left: 0.5rem;">{conf:.0%}</span>'
            
            # Expand the Chrome job (idx 1) after 3 seconds to simulate click
            if idx == 1 and job["id"] == "pkg-chrome-120" and should_expand_chrome:
                # Modal-style expanded card with comprehensive processing data
                meta = job.get("metadata", {})
                analysis = job.get("analysis", {})
                conf = analysis.get("confidence", 0)
                conf_color = "#00BA7C" if conf >= 0.8 else "#FFB347"
                install_cmd = analysis.get("install_command", "msiexec /i Chrome_Enterprise.msi /qn /norestart")
                switches = analysis.get("silent_switches", ["/qn", "/norestart"])
                switches_html = " ".join([f'<span style="background: rgba(255,107,53,0.2); color: #FF6B35; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">{s}</span>' for s in switches])
                
                st.markdown(f'<div style="background: linear-gradient(145deg, rgba(15,20,25,0.98) 0%, rgba(20,25,30,0.98) 100%); border: 2px solid rgba(255,107,53,0.6); border-radius: 16px; padding: 1.5rem; margin: 1rem 0 1.5rem 0; box-shadow: 0 0 40px rgba(255,107,53,0.2), inset 0 0 60px rgba(0,0,0,0.3);"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255,107,53,0.3);"><div style="display: flex; align-items: center; gap: 1rem;"><span style="font-size: 2rem;">✅</span><div><div style="font-size: 1.25rem; font-weight: 700; color: #F0F6FC;">{job["filename"]}</div><div style="font-size: 0.85rem; color: #8B949E;">Job ID: {job["id"]} • Processed in 2.3 min</div></div></div><span style="background: rgba(0,186,124,0.15); color: #00BA7C; padding: 0.4rem 0.75rem; border-radius: 6px; font-weight: 600; font-size: 0.8rem;">✓ Completed</span></div><div style="background: rgba(0,0,0,0.25); border-radius: 12px; padding: 1rem; margin-bottom: 1.25rem;"><div style="font-size: 0.7rem; color: #8B949E; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">Processing Timeline</div><div style="display: flex; gap: 0.5rem; flex-wrap: wrap;"><span style="background: rgba(0,186,124,0.15); color: #00BA7C; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.75rem;">✓ Upload</span><span style="color: #8B949E;">→</span><span style="background: rgba(0,186,124,0.15); color: #00BA7C; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.75rem;">✓ Hash Extracted</span><span style="color: #8B949E;">→</span><span style="background: rgba(0,186,124,0.15); color: #00BA7C; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.75rem;">✓ AI Analysis</span><span style="color: #8B949E;">→</span><span style="background: rgba(0,186,124,0.15); color: #00BA7C; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.75rem;">✓ Scripts Generated</span><span style="color: #8B949E;">→</span><span style="background: rgba(0,186,124,0.15); color: #00BA7C; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.75rem;">✓ WDAC Policy</span></div></div><div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.25rem;"><div style="background: rgba(0,0,0,0.3); border-radius: 12px; padding: 1rem;"><div style="font-size: 0.7rem; color: #8B949E; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">📋 Metadata Extracted</div><div style="display: grid; gap: 0.4rem; font-size: 0.85rem;"><div style="display: flex; justify-content: space-between;"><span style="color: #8B949E;">Product</span><span style="color: #F0F6FC; font-weight: 600;">{meta.get("product_name", "Google Chrome")}</span></div><div style="display: flex; justify-content: space-between;"><span style="color: #8B949E;">Version</span><span style="color: #F0F6FC;">{meta.get("product_version", "120.0.6099.130")}</span></div><div style="display: flex; justify-content: space-between;"><span style="color: #8B949E;">Manufacturer</span><span style="color: #F0F6FC;">{meta.get("manufacturer", "Google LLC")}</span></div><div style="display: flex; justify-content: space-between;"><span style="color: #8B949E;">Type</span><span style="background: rgba(255,107,53,0.2); color: #FF6B35; padding: 0.1rem 0.4rem; border-radius: 4px; font-size: 0.75rem;">MSI</span></div><div style="display: flex; justify-content: space-between;"><span style="color: #8B949E;">Size</span><span style="color: #F0F6FC;">84.2 MB</span></div><div style="display: flex; justify-content: space-between;"><span style="color: #8B949E;">Architecture</span><span style="color: #F0F6FC;">x64</span></div></div></div><div style="background: rgba(0,0,0,0.3); border-radius: 12px; padding: 1rem;"><div style="font-size: 0.7rem; color: #8B949E; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">🤖 AI Analysis</div><div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;"><div style="text-align: center;"><div style="font-size: 1.75rem; font-weight: 800; color: {conf_color};">{conf:.0%}</div><div style="font-size: 0.65rem; color: #8B949E;">Confidence</div></div><div style="flex: 1; font-size: 0.8rem; color: #8B949E; line-height: 1.4;">{analysis.get("reasoning", "Silent install verified. Standard MSI with enterprise switches.")}</div></div><div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 0.5rem; font-size: 0.75rem; color: #8B949E;"><span style="color: #00BA7C;">✓</span> 3 similar packages found in KB</div></div></div><div style="background: rgba(0,0,0,0.4); border-radius: 12px; padding: 1rem; border: 1px solid rgba(255,107,53,0.3); margin-bottom: 1.25rem;"><div style="font-size: 0.7rem; color: #8B949E; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">⚡ Install Command</div><div style="background: #0D1117; border-radius: 8px; padding: 0.75rem 1rem; font-family: monospace; font-size: 0.85rem; color: #FF6B35; font-weight: 600; overflow-x: auto;">{install_cmd}</div><div style="margin-top: 0.75rem; display: flex; align-items: center; gap: 0.5rem;"><span style="font-size: 0.75rem; color: #8B949E;">Detected Switches:</span>{switches_html}</div></div><div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem;"><div style="background: rgba(0,0,0,0.3); border-radius: 12px; padding: 1rem;"><div style="font-size: 0.7rem; color: #8B949E; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">📦 Generated Artifacts</div><div style="display: grid; gap: 0.4rem; font-size: 0.8rem;"><div style="display: flex; align-items: center; gap: 0.5rem;"><span style="color: #00BA7C;">✓</span><span style="color: #F0F6FC;">Install.ps1</span></div><div style="display: flex; align-items: center; gap: 0.5rem;"><span style="color: #00BA7C;">✓</span><span style="color: #F0F6FC;">Uninstall.ps1</span></div><div style="display: flex; align-items: center; gap: 0.5rem;"><span style="color: #00BA7C;">✓</span><span style="color: #F0F6FC;">Detection.ps1</span></div><div style="display: flex; align-items: center; gap: 0.5rem;"><span style="color: #00BA7C;">✓</span><span style="color: #F0F6FC;">package.json</span></div><div style="display: flex; align-items: center; gap: 0.5rem;"><span style="color: #00BA7C;">✓</span><span style="color: #F0F6FC;">WDAC_Policy.xml</span></div></div></div><div style="background: rgba(0,0,0,0.3); border-radius: 12px; padding: 1rem;"><div style="font-size: 0.7rem; color: #8B949E; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">🛡️ Compliance Checks</div><div style="display: grid; gap: 0.4rem; font-size: 0.8rem;"><div style="display: flex; align-items: center; gap: 0.5rem;"><span style="color: #00BA7C;">✓</span><span style="color: #F0F6FC;">Code Signing Verified</span></div><div style="display: flex; align-items: center; gap: 0.5rem;"><span style="color: #00BA7C;">✓</span><span style="color: #F0F6FC;">WDAC Hash Generated</span></div><div style="display: flex; align-items: center; gap: 0.5rem;"><span style="color: #00BA7C;">✓</span><span style="color: #F0F6FC;">Silent Install Tested</span></div><div style="display: flex; align-items: center; gap: 0.5rem;"><span style="color: #00BA7C;">✓</span><span style="color: #F0F6FC;">Intune Ready</span></div><div style="display: flex; align-items: center; gap: 0.5rem;"><span style="color: #00BA7C;">✓</span><span style="color: #F0F6FC;">No Known Vulnerabilities</span></div></div></div></div><div style="margin-top: 1rem; background: rgba(0,0,0,0.25); border-radius: 8px; padding: 0.75rem 1rem;"><div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem;"><span style="color: #8B949E;">SHA256:</span><code style="color: #58A6FF; font-family: monospace; font-size: 0.7rem;">a3f8c2b1e9d4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0</code></div></div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="glass-card {success_class}" style="margin-bottom: 0.75rem; padding: 1rem 1.25rem; {success_glow} {animation_delay}"><div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;"><div style="display: flex; align-items: center; gap: 0.75rem;"><span style="font-size: 1.25rem;">{icon}</span><span style="font-weight: 600; color: var(--forge-text);">{job["filename"]}</span>{confidence_html}</div><div style="display: flex; align-items: center; gap: 0.75rem;"><span class="badge {badge_class}">{job["status"].replace("_", " ")}</span><code style="font-size: 0.75rem; color: var(--forge-text-muted);">{job["id"]}</code></div></div></div>', unsafe_allow_html=True)
        else:
            with st.expander(f"{icon} **{job['filename']}** — `{job['id']}`", expanded=False):
                render_job_details(job["id"])


# ===== Search Page =====
def render_search_page():
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 class="hero-title" style="font-size: 2.5rem;">Search Knowledge Base</h1>
        <p class="hero-subtitle">Find similar packages or discover installation commands</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mock search results for demo
    MOCK_SEARCH_RESULTS = [
        {"product_name": "Google Chrome", "manufacturer": "Google LLC", "version": "120.0", "confidence": 0.95, "install_command": "msiexec /i Chrome_Enterprise.msi /qn /norestart"},
        {"product_name": "Microsoft Edge", "manufacturer": "Microsoft", "version": "119.0", "confidence": 0.92, "install_command": "msiexec /i MicrosoftEdge.msi /qn /norestart"},
        {"product_name": "Mozilla Firefox", "manufacturer": "Mozilla", "version": "121.0", "confidence": 0.88, "install_command": "Firefox_Setup.exe -ms"},
        {"product_name": "7-Zip", "manufacturer": "Igor Pavlov", "version": "23.01", "confidence": 0.96, "install_command": "msiexec /i 7z2301-x64.msi /qn"},
        {"product_name": "Notepad++", "manufacturer": "Don Ho", "version": "8.5", "confidence": 0.89, "install_command": "npp.8.5.Installer.x64.exe /S"},
    ]
    
    is_auto_demo = st.session_state.get('auto_demo', False)
    
    if is_auto_demo:
        # Show static demo results during auto-demo
        st.markdown('''
        <div class="glass-card-sm" style="margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-size: 1.25rem;">🔍</span>
            <span style="color: var(--forge-text-muted);">Search: "silent install"</span>
        </div>
        ''', unsafe_allow_html=True)
        
        st.success(f"Found **{len(MOCK_SEARCH_RESULTS)}** matching packages")
        
        for r in MOCK_SEARCH_RESULTS:
            confidence = r.get("confidence", 0)
            conf_color = "var(--forge-success)" if confidence >= 0.8 else "var(--forge-warning)" if confidence >= 0.6 else "var(--forge-error)"
            
            st.markdown(f"""
            <div class="glass-card" style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1.5rem; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 200px;">
                        <div style="font-weight: 700; font-size: 1.1rem; color: var(--forge-text); margin-bottom: 0.25rem;">
                            {r.get('product_name', 'Unknown')}
                        </div>
                        <div style="font-size: 0.85rem; color: var(--forge-text-muted);">
                            {r.get('manufacturer', 'Unknown')} • v{r.get('version', 'Unknown')}
                        </div>
                        <code style="display: block; margin-top: 0.75rem; padding: 0.5rem; background: rgba(0,0,0,0.3); border-radius: 8px; font-size: 0.8rem; color: var(--forge-orange);">{r.get('install_command', '')}</code>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: {conf_color};">{confidence:.0%}</div>
                        <div style="font-size: 0.7rem; color: var(--forge-text-muted);">match</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        query = st.text_input("🔍 Search", placeholder="e.g., Chrome, Adobe, silent install, /qn", label_visibility="collapsed", key="search_query")
        
        if query:
            with st.spinner("Searching..."):
                if DEMO_MODE:
                    # Filter mock results based on query
                    query_lower = query.lower()
                    filtered = [r for r in MOCK_SEARCH_RESULTS if query_lower in r["product_name"].lower() or query_lower in r["manufacturer"].lower() or query_lower in r["install_command"].lower()]
                    results = {"results": filtered if filtered else MOCK_SEARCH_RESULTS[:3]}
                else:
                    results = search_knowledge(query)
            
            if results.get("results"):
                st.success(f"Found **{len(results['results'])}** matching packages")
                
                for r in results["results"]:
                    confidence = r.get("confidence", 0)
                    if confidence >= 0.8:
                        conf_color = "var(--forge-success)"
                    elif confidence >= 0.6:
                        conf_color = "var(--forge-warning)"
                    else:
                        conf_color = "var(--forge-error)"
                    
                    st.markdown(f"""
                    <div class="glass-card" style="margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1.5rem;">
                            <div style="flex: 1;">
                                <div style="font-weight: 700; font-size: 1.1rem; color: var(--forge-text); margin-bottom: 0.25rem;">
                                    {r.get('product_name', r.get('filename', 'Unknown'))}
                                </div>
                                <div style="font-size: 0.85rem; color: var(--forge-text-muted);">
                                    {r.get('manufacturer', 'Unknown')} • v{r.get('version', 'Unknown')}
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 1.5rem; font-weight: 700; color: {conf_color};">{confidence:.0%}</div>
                                <div style="font-size: 0.7rem; color: var(--forge-text-muted);">match</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if r.get("install_command"):
                        st.code(r["install_command"], language="powershell")
            else:
                st.info("No results found. Try a different search term.")
        else:
            stats = MOCK_STATS if DEMO_MODE else get_knowledge_stats()
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="metric-card" style="--metric-color: var(--forge-orange); padding: 2rem;">
                    <div class="metric-value" style="font-size: 3.5rem; color: var(--forge-orange);">{stats.get('total_packages', 247)}</div>
                    <div class="metric-label">Indexed Applications</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card" style="--metric-color: var(--forge-info); padding: 2rem;">
                    <div class="metric-value" style="font-size: 3.5rem; color: var(--forge-info);">{stats.get('total_commands', 1892)}</div>
                    <div class="metric-label">Known Install Commands</div>
                </div>
                """, unsafe_allow_html=True)


# ===== Impact Page (NEW - VC focused) =====
def render_impact_page():
    """VC-focused page showing market opportunity and ROI metrics"""
    
    st.markdown("""
    <div class="page-fade-in" style="text-align: center; margin-bottom: 2.5rem;">
        <h1 class="hero-title" style="font-size: 2.75rem;">Market Opportunity</h1>
        <p class="hero-subtitle">Transforming enterprise endpoint management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Big Impact Numbers Row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align: center; border-color: rgba(255,107,53,0.3); padding: 2rem;">
            <div class="impact-number impact-number-delay-1" style="font-size: 3.5rem; font-weight: 900; background: linear-gradient(135deg, #FF6B35 0%, #FFB347 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">$4.2B</div>
            <div style="font-size: 0.9rem; color: var(--forge-text-muted); margin-top: 0.5rem;">Total Addressable Market</div>
            <div style="font-size: 0.75rem; color: var(--forge-orange); margin-top: 0.25rem;">Endpoint Management Software</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align: center; border-color: rgba(255,107,53,0.3); padding: 2rem;">
            <div class="impact-number impact-number-delay-2" style="font-size: 3.5rem; font-weight: 900; background: linear-gradient(135deg, #FF6B35 0%, #FFB347 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">50K+</div>
            <div style="font-size: 0.9rem; color: var(--forge-text-muted); margin-top: 0.5rem;">Enterprise IT Teams</div>
            <div style="font-size: 0.75rem; color: var(--forge-orange); margin-top: 0.25rem;">Struggling with app packaging</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="glass-card" style="text-align: center; border-color: rgba(255,107,53,0.3); padding: 2rem;">
            <div class="impact-number impact-number-delay-3" style="font-size: 3.5rem; font-weight: 900; background: linear-gradient(135deg, #FF6B35 0%, #FFB347 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">156h</div>
            <div style="font-size: 0.9rem; color: var(--forge-text-muted); margin-top: 0.5rem;">Saved Per Quarter</div>
            <div style="font-size: 0.75rem; color: var(--forge-orange); margin-top: 0.25rem;">Per enterprise customer</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
    
    # ROI Breakdown
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown('<div class="section-title">Customer ROI</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <span style="color: var(--forge-text-muted);">Time Savings</span>
                <span style="font-weight: 700; color: var(--forge-success);">87% reduction</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <span style="color: var(--forge-text-muted);">Error Rate</span>
                <span style="font-weight: 700; color: var(--forge-success);">94% accuracy</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <span style="color: var(--forge-text-muted);">Compliance Ready</span>
                <span style="font-weight: 700; color: var(--forge-success);">100% WDAC</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0;">
                <span style="color: var(--forge-text-muted);">Annual Value</span>
                <span style="font-weight: 700; color: var(--forge-orange);">$125K+ saved</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="section-title">Why Now?</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card">
            <div style="display: flex; align-items: flex-start; gap: 1rem; padding: 0.75rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <span style="font-size: 1.5rem;">🛡️</span>
                <div>
                    <div style="font-weight: 600; color: var(--forge-text);">WDAC Mandates</div>
                    <div style="font-size: 0.8rem; color: var(--forge-text-muted);">Zero-trust security requirements accelerating</div>
                </div>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 1rem; padding: 0.75rem 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <span style="font-size: 1.5rem;">🤖</span>
                <div>
                    <div style="font-weight: 600; color: var(--forge-text);">AI Breakthrough</div>
                    <div style="font-size: 0.8rem; color: var(--forge-text-muted);">LLMs enable automated switch discovery</div>
                </div>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 1rem; padding: 0.75rem 0;">
                <span style="font-size: 1.5rem;">📈</span>
                <div>
                    <div style="font-weight: 600; color: var(--forge-text);">App Explosion</div>
                    <div style="font-size: 0.8rem; color: var(--forge-text-muted);">SaaS proliferation straining IT teams</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
    
    # Competitive Advantage
    st.markdown('<div class="section-title">Competitive Moat</div>', unsafe_allow_html=True)
    
    col_a, col_b, col_c, col_d = st.columns(4)
    
    with col_a:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 1.25rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🧠</div>
            <div style="font-weight: 600; font-size: 0.9rem; color: var(--forge-text);">RAG Knowledge</div>
            <div style="font-size: 0.75rem; color: var(--forge-text-muted); margin-top: 0.25rem;">1,800+ commands indexed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 1.25rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔄</div>
            <div style="font-weight: 600; font-size: 0.9rem; color: var(--forge-text);">Network Effects</div>
            <div style="font-size: 0.75rem; color: var(--forge-text-muted); margin-top: 0.25rem;">Each package improves AI</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_c:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 1.25rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">☁️</div>
            <div style="font-weight: 600; font-size: 0.9rem; color: var(--forge-text);">Azure Native</div>
            <div style="font-size: 0.75rem; color: var(--forge-text-muted); margin-top: 0.25rem;">Intune + Entra integrated</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_d:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 1.25rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
            <div style="font-weight: 600; font-size: 0.9rem; color: var(--forge-text);">First Mover</div>
            <div style="font-size: 0.75rem; color: var(--forge-text-muted); margin-top: 0.25rem;">AI-first packaging</div>
        </div>
        """, unsafe_allow_html=True)


# ===== Dashboard =====
def render_dashboard():
    is_auto_demo = st.session_state.get('auto_demo', False)
    count_class = "count-up" if is_auto_demo else ""
    impact_class = "impact-number" if is_auto_demo else ""
    
    # Hero Section with Impact Focus
    st.markdown("""
    <div class="page-fade-in" style="text-align: center; margin-bottom: 1.5rem;">
        <h1 class="hero-title" style="font-size: 2.5rem;">Command Center</h1>
        <p class="hero-subtitle">Real-time insights & business impact</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Use mock data in demo mode
    jobs = MOCK_JOBS if DEMO_MODE else get_all_jobs()
    stats = MOCK_STATS if DEMO_MODE else get_knowledge_stats()
    
    completed = len([j for j in jobs if j["status"] == "completed"])
    pending = len([j for j in jobs if j["status"] in ["pending", "analyzing", "packaging"]])
    needs_review = len([j for j in jobs if j["status"] == "needs_review"])
    
    # ===== HERO IMPACT ROW - Big Numbers =====
    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    
    with col_h1:
        st.markdown(f'<div class="glass-card" style="text-align: center; background: linear-gradient(135deg, rgba(255,107,53,0.08) 0%, rgba(255,179,71,0.04) 100%); border-color: rgba(255,107,53,0.2);"><div class="{impact_class} impact-number-delay-1" style="font-size: 2.5rem; font-weight: 900; background: linear-gradient(135deg, #FF6B35 0%, #FFB347 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{stats.get("time_saved_hours", 156)}h</div><div style="font-size: 0.8rem; color: var(--forge-text-muted); margin-top: 0.25rem;">Time Saved</div><div style="font-size: 0.7rem; color: var(--forge-success); margin-top: 0.15rem;">↑ vs manual</div></div>', unsafe_allow_html=True)
    
    with col_h2:
        st.markdown(f'<div class="glass-card" style="text-align: center; background: linear-gradient(135deg, rgba(0,186,124,0.08) 0%, rgba(52,211,153,0.04) 100%); border-color: rgba(0,186,124,0.2);"><div class="{impact_class} impact-number-delay-2" style="font-size: 2.5rem; font-weight: 900; background: linear-gradient(135deg, #00BA7C 0%, #34D399 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{stats.get("success_rate", 94.2)}%</div><div style="font-size: 0.8rem; color: var(--forge-text-muted); margin-top: 0.25rem;">Success Rate</div><div style="font-size: 0.7rem; color: var(--forge-success); margin-top: 0.15rem;">First-time accuracy</div></div>', unsafe_allow_html=True)
    
    with col_h3:
        st.markdown(f'<div class="glass-card" style="text-align: center; background: linear-gradient(135deg, rgba(255,107,53,0.08) 0%, rgba(255,179,71,0.04) 100%); border-color: rgba(255,107,53,0.2);"><div class="{impact_class} impact-number-delay-3" style="font-size: 2.5rem; font-weight: 900; background: linear-gradient(135deg, #FF6B35 0%, #FFB347 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">$125K</div><div style="font-size: 0.8rem; color: var(--forge-text-muted); margin-top: 0.25rem;">Annual Savings</div><div style="font-size: 0.7rem; color: var(--forge-success); margin-top: 0.15rem;">Per enterprise</div></div>', unsafe_allow_html=True)
    
    with col_h4:
        st.markdown(f'<div class="glass-card" style="text-align: center; background: linear-gradient(135deg, rgba(59,130,246,0.08) 0%, rgba(96,165,250,0.04) 100%); border-color: rgba(59,130,246,0.2);"><div class="{impact_class}" style="font-size: 2.5rem; font-weight: 900; background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{stats.get("total_commands", 1892)}</div><div style="font-size: 0.8rem; color: var(--forge-text-muted); margin-top: 0.25rem;">Commands Known</div><div style="font-size: 0.7rem; color: var(--forge-info); margin-top: 0.15rem;">RAG knowledge base</div></div>', unsafe_allow_html=True)
    
    # ===== OPERATIONS STATUS ROW =====
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<div class="metric-card success-burst" style="--metric-color: var(--forge-success);"><div class="metric-value {count_class} count-up-delay-1" style="color: var(--forge-success);">{completed}</div><div class="metric-label">Completed</div></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="metric-card" style="--metric-color: var(--forge-info);"><div class="metric-value {count_class} count-up-delay-2" style="color: var(--forge-info);">{pending}</div><div class="metric-label">In Progress</div></div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="metric-card" style="--metric-color: var(--forge-warning);"><div class="metric-value {count_class} count-up-delay-3" style="color: var(--forge-warning);">{needs_review}</div><div class="metric-label">Review</div></div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'<div class="metric-card" style="--metric-color: var(--forge-orange);"><div class="metric-value {count_class} count-up-delay-4" style="color: var(--forge-orange);">{stats.get("total_packages", 247)}</div><div class="metric-label">Total Packages</div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
    
    # ===== BEFORE/AFTER + ROI ROW =====
    col_ba, col_roi = st.columns([1, 1])
    
    with col_ba:
        st.markdown('<div class="section-title">Efficiency Gains</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card" style="padding: 1.25rem;"><div style="display: flex; gap: 1rem;"><div style="flex: 1; background: linear-gradient(145deg, rgba(244, 33, 46, 0.05) 0%, transparent 100%); border: 1px solid rgba(244, 33, 46, 0.2); border-radius: 12px; padding: 1rem; text-align: center;"><div style="font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--forge-error); margin-bottom: 0.5rem;">❌ Manual</div><div style="font-size: 1.75rem; font-weight: 800; color: var(--forge-error);">4-6h</div><div style="font-size: 0.7rem; color: var(--forge-text-muted);">per package</div></div><div style="display: flex; align-items: center; color: var(--forge-orange); font-size: 1.5rem;">→</div><div style="flex: 1; background: linear-gradient(145deg, rgba(0, 186, 124, 0.08) 0%, transparent 100%); border: 1px solid rgba(0, 186, 124, 0.3); border-radius: 12px; padding: 1rem; text-align: center;"><div style="font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--forge-success); margin-bottom: 0.5rem;">✓ Forge</div><div style="font-size: 1.75rem; font-weight: 800; color: var(--forge-success);">2.3m</div><div style="font-size: 0.7rem; color: var(--forge-text-muted);">automated</div></div></div><div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); text-align: center;"><span style="font-size: 1.5rem; font-weight: 800; color: var(--forge-orange);">87%</span><span style="font-size: 0.85rem; color: var(--forge-text-muted); margin-left: 0.5rem;">time reduction</span></div></div>', unsafe_allow_html=True)
    
    with col_roi:
        st.markdown('<div class="section-title">Customer ROI</div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card" style="padding: 1.25rem;"><div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.08);"><span style="color: var(--forge-text-muted); font-size: 0.85rem;">⏱️ Time Savings</span><span style="font-weight: 700; color: var(--forge-success);">87% reduction</span></div><div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.08);"><span style="color: var(--forge-text-muted); font-size: 0.85rem;">🎯 First-Time Accuracy</span><span style="font-weight: 700; color: var(--forge-success);">94%</span></div><div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.08);"><span style="color: var(--forge-text-muted); font-size: 0.85rem;">🛡️ WDAC Compliance</span><span style="font-weight: 700; color: var(--forge-success);">100%</span></div><div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0;"><span style="color: var(--forge-text-muted); font-size: 0.85rem;">💰 Annual Value</span><span style="font-weight: 700; color: var(--forge-orange);">$125K+ saved</span></div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
    
    # ===== MARKET OPPORTUNITY ROW (VC Focus) =====
    st.markdown('<div class="section-title">Market Opportunity</div>', unsafe_allow_html=True)
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    with col_m1:
        st.markdown(f'<div class="glass-card" style="text-align: center; border-color: rgba(255,107,53,0.2); padding: 1.25rem;"><div class="{impact_class}" style="font-size: 2rem; font-weight: 900; color: var(--forge-orange);">$4.2B</div><div style="font-size: 0.75rem; color: var(--forge-text-muted); margin-top: 0.25rem;">TAM</div><div style="font-size: 0.65rem; color: var(--forge-orange); margin-top: 0.15rem;">Endpoint Mgmt</div></div>', unsafe_allow_html=True)
    
    with col_m2:
        st.markdown(f'<div class="glass-card" style="text-align: center; border-color: rgba(255,107,53,0.2); padding: 1.25rem;"><div class="{impact_class}" style="font-size: 2rem; font-weight: 900; color: var(--forge-orange);">50K+</div><div style="font-size: 0.75rem; color: var(--forge-text-muted); margin-top: 0.25rem;">IT Teams</div><div style="font-size: 0.65rem; color: var(--forge-orange); margin-top: 0.15rem;">Target market</div></div>', unsafe_allow_html=True)
    
    with col_m3:
        st.markdown('<div class="glass-card" style="text-align: center; border-color: rgba(255,107,53,0.2); padding: 1.25rem;"><div style="font-size: 2rem; font-weight: 900; color: var(--forge-success);">🛡️</div><div style="font-size: 0.75rem; color: var(--forge-text-muted); margin-top: 0.25rem;">WDAC Mandates</div><div style="font-size: 0.65rem; color: var(--forge-success); margin-top: 0.15rem;">Accelerating</div></div>', unsafe_allow_html=True)
    
    with col_m4:
        st.markdown('<div class="glass-card" style="text-align: center; border-color: rgba(255,107,53,0.2); padding: 1.25rem;"><div style="font-size: 2rem; font-weight: 900; color: var(--forge-info);">🤖</div><div style="font-size: 0.75rem; color: var(--forge-text-muted); margin-top: 0.25rem;">AI-First</div><div style="font-size: 0.65rem; color: var(--forge-info); margin-top: 0.15rem;">First mover</div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="forge-divider"></div>', unsafe_allow_html=True)
    
    # ===== ACTIVITY ROW =====
    col_jobs, col_chart = st.columns([1, 1])
    
    with col_jobs:
        st.markdown('<div class="section-title">Recent Activity</div>', unsafe_allow_html=True)
        
        if jobs:
            jobs_html = '<div class="jobs-list">'
            for idx, job in enumerate(jobs[:5]):
                icon_map = {"completed": "✅", "analyzing": "🔍", "pending": "⏳", "failed": "❌", "needs_review": "⚠️", "packaging": "📦"}
                icon = icon_map.get(job["status"], "⏳")
                is_completed = job["status"] == "completed"
                glow = "border-color: rgba(0,186,124,0.3);" if is_completed else ""
                conf_html = ""
                if is_completed and job.get("analysis"):
                    conf = job["analysis"].get("confidence", 0)
                    conf_color = "var(--forge-success)" if conf >= 0.8 else "var(--forge-warning)"
                    conf_html = f'<span style="font-size: 0.7rem; font-weight: 600; color: {conf_color};">{conf:.0%}</span>'
                
                jobs_html += f'<div class="glass-card-sm" style="margin-bottom: 0.5rem; {glow}"><div style="display: flex; align-items: center; gap: 0.5rem;"><span>{icon}</span><span style="font-weight: 500; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 140px;">{job["filename"]}</span>{conf_html}</div></div>'
            jobs_html += '</div>'
            st.markdown(jobs_html, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color: var(--forge-text-muted); text-align: center; padding: 2rem;">No recent jobs</div>', unsafe_allow_html=True)
    
    with col_chart:
        st.markdown('<div class="section-title">Weekly Trend</div>', unsafe_allow_html=True)
        weekly = stats.get('weekly_trend', [28, 31, 25, 42, 38, 34, 29])
        days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        max_val = max(weekly)
        total_week = sum(weekly)
        
        bar_items = ""
        for i, (day, val) in enumerate(zip(days, weekly)):
            height_pct = (val / max_val * 100) if max_val > 0 else 0
            today = i == 6
            color = 'linear-gradient(180deg, #FF6B35 0%, #FFB347 100%)' if today else 'linear-gradient(180deg, rgba(255,107,53,0.6) 0%, rgba(255,179,71,0.4) 100%)'
            bar_items += f'<div style="text-align: center; flex: 1;"><div style="font-size: 0.65rem; color: var(--forge-text-muted); margin-bottom: 0.25rem;">{val}</div><div style="height: {height_pct}%; min-height: 8px; background: {color}; border-radius: 4px 4px 0 0; margin: 0 3px;"></div><div style="font-size: 0.6rem; color: var(--forge-text-muted); margin-top: 0.25rem;">{day}</div></div>'
        
        st.markdown(f'<div class="glass-card"><div style="display: flex; align-items: flex-end; justify-content: space-between; height: 100px; padding: 0.5rem 0;">{bar_items}</div><div style="text-align: center; margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid rgba(255,255,255,0.1);"><span style="font-size: 1.25rem; font-weight: 700; color: var(--forge-orange);">{total_week}</span><span style="font-size: 0.8rem; color: var(--forge-text-muted); margin-left: 0.5rem;">packages this week</span></div></div>', unsafe_allow_html=True)


# ===== Main =====
def main():
    page = render_sidebar()
    
    # Auto-demo banner when active - VC optimized
    is_auto_demo = st.session_state.get('auto_demo', False)
    if is_auto_demo:
        current_idx = st.session_state.get('demo_page_index', 0)
        current_page = AUTO_DEMO_PAGES[current_idx % len(AUTO_DEMO_PAGES)]
        page_interval = AUTO_DEMO_PAGE_TIMES.get(current_page, AUTO_DEMO_INTERVAL)
        demo_time = st.session_state.get('demo_start_time', time.time())
        caption = DEMO_CAPTIONS.get(current_page, {"headline": "", "subtext": ""})
        elapsed = time.time() - demo_time
        progress_pct = min(100, (elapsed / page_interval) * 100)
        
        # Sleek top banner with progress
        st.markdown(f'<div style="position: fixed; top: 0; left: 0; right: 0; z-index: 9999; background: linear-gradient(180deg, rgba(15,20,25,0.98) 0%, rgba(15,20,25,0.95) 100%); border-bottom: 1px solid rgba(255,107,53,0.3);"><div style="height: 3px; background: rgba(255,255,255,0.1);"><div style="height: 100%; width: {progress_pct}%; background: linear-gradient(90deg, #FF6B35, #FFB347); transition: width 0.3s ease;"></div></div></div><div style="height: 8px;"></div>', unsafe_allow_html=True)
        
        # Floating VC Caption Overlay - bottom left
        st.markdown(f'<div class="vc-caption-overlay" style="position: fixed; bottom: 30px; left: 30px; z-index: 9998; max-width: 400px;"><div style="background: rgba(15,20,25,0.95); backdrop-filter: blur(20px); border: 1px solid rgba(255,107,53,0.4); border-radius: 16px; padding: 1.25rem 1.5rem; box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 30px rgba(255,107,53,0.15);"><div style="font-size: 1.5rem; font-weight: 800; color: #FF6B35; letter-spacing: -0.02em; margin-bottom: 0.25rem;">{caption["headline"]}</div><div style="font-size: 0.95rem; color: rgba(231,233,234,0.85); font-weight: 400;">{caption["subtext"]}</div></div></div>', unsafe_allow_html=True)
        
        # Immediately scroll to top when page changes - unique timestamp forces re-execution
        scroll_top_js = f'''
        <script>
            // Page: {current_idx}, Time: {demo_time}
            (function() {{
                const mainContent = window.parent.document.querySelector('section.main');
                if (mainContent) {{
                    mainContent.scrollTop = 0;
                    setTimeout(() => {{ mainContent.scrollTop = 0; }}, 50);
                    setTimeout(() => {{ mainContent.scrollTop = 0; }}, 150);
                }}
            }})();
        </script>
        '''
        components.html(scroll_top_js, height=0)
    
    if "Upload" in page:
        render_upload_page()
    elif "Jobs" in page:
        render_jobs_page()
    elif "Search" in page:
        render_search_page()
    elif "Dashboard" in page:
        render_dashboard()
    
    # Auto-scroll AFTER content is rendered (so we know the full height)
    if is_auto_demo:
        current_idx = st.session_state.get('demo_page_index', 0)
        current_page = AUTO_DEMO_PAGES[current_idx % len(AUTO_DEMO_PAGES)]
        page_interval = AUTO_DEMO_PAGE_TIMES.get(current_page, AUTO_DEMO_INTERVAL)
        demo_time = st.session_state.get('demo_start_time', time.time())
        scroll_js = f'''
        <script>
            // Smooth scroll - Page: {current_idx}, Time: {demo_time}
            (function() {{
                const scrollDuration = {page_interval * 1000 - 800};
                const mainContent = window.parent.document.querySelector('section.main');
                if (mainContent) {{
                    // Wait for content to fully render
                    setTimeout(() => {{
                        const scrollHeight = mainContent.scrollHeight - mainContent.clientHeight;
                        let startTime = null;
                        
                        function smoothScroll(timestamp) {{
                            if (!startTime) startTime = timestamp;
                            const elapsed = timestamp - startTime;
                            const progress = Math.min(elapsed / scrollDuration, 1);
                            const easeProgress = progress < 0.5 
                                ? 2 * progress * progress 
                                : 1 - Math.pow(-2 * progress + 2, 2) / 2;
                            mainContent.scrollTop = easeProgress * scrollHeight;
                            if (progress < 1) {{
                                requestAnimationFrame(smoothScroll);
                            }}
                        }}
                        
                        requestAnimationFrame(smoothScroll);
                    }}, 300);
                }}
            }})();
        </script>
        '''
        components.html(scroll_js, height=0)
    
    # Auto-demo timer - uses streamlit-autorefresh for reliable page transitions
    if st.session_state.get('auto_demo', False):
        # Auto-refresh every second to update countdown and check for page change
        st_autorefresh(interval=1000, limit=None, key="demo_refresh")
        
        # Use nav_options length (3 pages - no Search in demo)
        nav_options = ["🏠  Upload", "📦  Jobs", "📊  Dashboard"]
        num_pages = len(nav_options)
        
        # Get per-page timing
        current_idx = st.session_state.get('demo_page_index', 0)
        current_page = nav_options[current_idx % num_pages]
        page_interval = AUTO_DEMO_PAGE_TIMES.get(current_page, AUTO_DEMO_INTERVAL)
        
        elapsed = time.time() - st.session_state.get('demo_start_time', time.time())
        remaining = page_interval - elapsed
        
        if remaining <= 0:
            # Time to change page
            new_idx = (current_idx + 1) % num_pages
            new_time = time.time()
            st.session_state.demo_page_index = new_idx
            st.session_state.demo_start_time = new_time
            st.query_params['idx'] = str(new_idx)
            st.query_params['t'] = str(new_time)
        
        # Minimal page indicator - bottom right (less distracting for VC)
        page_dots = " ".join([f'<div style="width: 8px; height: 8px; border-radius: 50%; background: {"var(--forge-orange)" if i == st.session_state.get("demo_page_index", 0) else "rgba(255,255,255,0.2)"};"></div>' for i in range(num_pages)])
        st.markdown(f'<div style="position: fixed; bottom: 30px; right: 30px; z-index: 9997;"><div style="display: flex; align-items: center; gap: 0.5rem;">{page_dots}</div></div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
