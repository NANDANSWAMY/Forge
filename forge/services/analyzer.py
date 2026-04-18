"""Forge POC - AI-Powered Installer Analyzer"""

import hashlib
import logging
from pathlib import Path
from typing import Optional

from openai import AzureOpenAI, OpenAI

from forge.config import settings
from forge.models import InstallerMetadata, InstallerType, AIAnalysisResult

logger = logging.getLogger(__name__)


# Common silent install switches by installer type
COMMON_SWITCHES = {
    InstallerType.MSI: ["/qn", "/quiet", "/passive", "/norestart", "ALLUSERS=1"],
    InstallerType.EXE: ["/S", "/s", "/silent", "/quiet", "-silent", "-quiet", "/VERYSILENT"],
    InstallerType.MSIX: [],  # MSIX are typically silent by default
}


ANALYSIS_PROMPT = """You are an expert Windows application packaging engineer. Analyze this installer and provide packaging information.

## Installer Information
- Filename: {filename}
- Type: {installer_type}
- Product Name: {product_name}
- Manufacturer: {manufacturer}
- Version: {product_version}

## Your Task
Determine the correct silent installation switches for this application.

Think step by step:
1. Identify the installer framework (MSI, InstallShield, NSIS, Inno Setup, WiX, etc.)
2. Based on the framework, determine the silent switches
3. Consider common vendor-specific requirements
4. Note any known issues or special considerations

## Output Format (JSON)
{{
    "silent_switches": ["list", "of", "switches"],
    "install_command": "full msiexec or exe command with switches",
    "uninstall_command": "command to uninstall silently",
    "confidence": 0.0 to 1.0,
    "reasoning": "brief explanation of your analysis",
    "known_issues": ["any known issues or gotchas"]
}}

Respond ONLY with valid JSON, no markdown formatting."""


class InstallerAnalyzer:
    """AI-powered installer analysis service."""
    
    def __init__(self):
        """Initialize the analyzer with OpenAI client."""
        if settings.use_azure:
            self.client = AzureOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
            )
            self.model = settings.azure_openai_deployment
        elif settings.openai_api_key:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = "gpt-4o"
        else:
            logger.warning("No OpenAI credentials configured - using mock responses")
            self.client = None
            self.model = None
    
    async def extract_metadata(self, file_path: Path) -> InstallerMetadata:
        """Extract metadata from an installer file."""
        filename = file_path.name
        installer_type = self._get_installer_type(filename)
        
        # Calculate file hash
        file_hash = await self._calculate_hash(file_path)
        
        # Extract metadata based on type
        metadata = InstallerMetadata(
            filename=filename,
            file_size=file_path.stat().st_size,
            installer_type=installer_type,
            file_hash=file_hash,
            detected_switches=COMMON_SWITCHES.get(installer_type, []),
        )
        
        # Try to extract more metadata based on installer type
        if installer_type == InstallerType.MSI:
            metadata = await self._extract_msi_metadata(file_path, metadata)
        elif installer_type == InstallerType.EXE:
            metadata = await self._extract_exe_metadata(file_path, metadata)
        
        return metadata
    
    async def analyze_installer(
        self, 
        file_path: Path, 
        metadata: InstallerMetadata
    ) -> AIAnalysisResult:
        """Use AI to analyze the installer and determine packaging parameters."""
        
        if not self.client:
            # Mock response for testing without API keys
            return self._mock_analysis(metadata)
        
        prompt = ANALYSIS_PROMPT.format(
            filename=metadata.filename,
            installer_type=metadata.installer_type.value,
            product_name=metadata.product_name or "Unknown",
            manufacturer=metadata.manufacturer or "Unknown",
            product_version=metadata.product_version or "Unknown",
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Windows application packaging engineer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result_json = response.choices[0].message.content
            import json
            result_data = json.loads(result_json)
            
            return AIAnalysisResult(
                silent_switches=result_data.get("silent_switches", []),
                install_command=result_data.get("install_command", ""),
                uninstall_command=result_data.get("uninstall_command", ""),
                confidence=result_data.get("confidence", 0.5),
                reasoning=result_data.get("reasoning", ""),
                known_issues=result_data.get("known_issues", []),
            )
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Fallback to basic analysis
            return self._basic_analysis(metadata)
    
    def _get_installer_type(self, filename: str) -> InstallerType:
        """Determine installer type from filename."""
        suffix = Path(filename).suffix.lower()
        return {
            ".msi": InstallerType.MSI,
            ".exe": InstallerType.EXE,
            ".msix": InstallerType.MSIX,
        }.get(suffix, InstallerType.UNKNOWN)
    
    async def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    async def _extract_msi_metadata(
        self, 
        file_path: Path, 
        metadata: InstallerMetadata
    ) -> InstallerMetadata:
        """Extract metadata from MSI file."""
        try:
            # Try using msitools or Windows COM
            # For POC, we'll parse what we can
            import subprocess
            
            # Try msiinfo on macOS/Linux, or platform-specific approach
            result = subprocess.run(
                ["msiinfo", "export", str(file_path), "Property"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        key, value = parts[0], parts[1]
                        if key == "ProductName":
                            metadata.product_name = value
                        elif key == "Manufacturer":
                            metadata.manufacturer = value
                        elif key == "ProductVersion":
                            metadata.product_version = value
        except Exception as e:
            logger.debug(f"Could not extract MSI metadata: {e}")
            # Fallback: try to infer from filename
            metadata = self._infer_from_filename(metadata)
        
        return metadata
    
    async def _extract_exe_metadata(
        self, 
        file_path: Path, 
        metadata: InstallerMetadata
    ) -> InstallerMetadata:
        """Extract metadata from EXE file."""
        try:
            import pefile
            pe = pefile.PE(str(file_path))
            
            if hasattr(pe, 'VS_FIXEDFILEINFO'):
                version_info = pe.VS_FIXEDFILEINFO[0]
                if version_info:
                    ms = version_info.FileVersionMS
                    ls = version_info.FileVersionLS
                    metadata.product_version = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
            
            # Try to get string info
            if hasattr(pe, 'FileInfo'):
                for file_info in pe.FileInfo:
                    for entry in file_info:
                        if hasattr(entry, 'StringTable'):
                            for st in entry.StringTable:
                                for key, value in st.entries.items():
                                    key_decoded = key.decode('utf-8', errors='ignore')
                                    value_decoded = value.decode('utf-8', errors='ignore')
                                    if key_decoded == 'ProductName':
                                        metadata.product_name = value_decoded
                                    elif key_decoded == 'CompanyName':
                                        metadata.manufacturer = value_decoded
            
            pe.close()
        except Exception as e:
            logger.debug(f"Could not extract EXE metadata: {e}")
            metadata = self._infer_from_filename(metadata)
        
        return metadata
    
    def _infer_from_filename(self, metadata: InstallerMetadata) -> InstallerMetadata:
        """Infer product info from filename."""
        # Common patterns: ProductName_1.2.3_x64.msi, ProductName-Setup-1.2.3.exe
        import re
        
        filename = metadata.filename
        # Remove extension
        name = Path(filename).stem
        
        # Try to extract version
        version_match = re.search(r'[\d]+\.[\d]+\.?[\d]*\.?[\d]*', name)
        if version_match:
            metadata.product_version = version_match.group()
            name = name.replace(version_match.group(), "")
        
        # Clean up name
        name = re.sub(r'[-_](setup|install|installer|x64|x86|amd64|win64|win32)', '', name, flags=re.IGNORECASE)
        name = name.strip("-_ ")
        
        if name and not metadata.product_name:
            metadata.product_name = name
        
        return metadata
    
    def _mock_analysis(self, metadata: InstallerMetadata) -> AIAnalysisResult:
        """Mock analysis for testing without API keys."""
        logger.info("Using mock AI analysis (no API keys configured)")
        
        if metadata.installer_type == InstallerType.MSI:
            return AIAnalysisResult(
                silent_switches=["/qn", "/norestart", "ALLUSERS=1"],
                install_command=f'msiexec /i "{metadata.filename}" /qn /norestart ALLUSERS=1',
                uninstall_command=f'msiexec /x "{metadata.filename}" /qn /norestart',
                confidence=0.85,
                reasoning="Standard MSI installer detected. Using standard Windows Installer silent switches.",
                known_issues=["Requires elevated privileges", "May require reboot"],
            )
        else:
            return AIAnalysisResult(
                silent_switches=["/S", "/VERYSILENT", "/NORESTART"],
                install_command=f'"{metadata.filename}" /S /NORESTART',
                uninstall_command="Check Add/Remove Programs for uninstall string",
                confidence=0.6,
                reasoning="EXE installer detected. Trying common silent switches. Manual verification recommended.",
                known_issues=["Installer framework unknown", "Silent switches may vary"],
            )
    
    def _basic_analysis(self, metadata: InstallerMetadata) -> AIAnalysisResult:
        """Basic analysis fallback."""
        switches = COMMON_SWITCHES.get(metadata.installer_type, [])
        
        if metadata.installer_type == InstallerType.MSI:
            cmd = f'msiexec /i "{metadata.filename}" {" ".join(switches)}'
            uncmd = f'msiexec /x "{metadata.filename}" /qn'
        else:
            cmd = f'"{metadata.filename}" {" ".join(switches[:2])}'
            uncmd = "Unknown"
        
        return AIAnalysisResult(
            silent_switches=switches,
            install_command=cmd,
            uninstall_command=uncmd,
            confidence=0.4,
            reasoning="Basic analysis based on installer type. AI analysis unavailable.",
            known_issues=["AI analysis failed - manual review recommended"],
        )
