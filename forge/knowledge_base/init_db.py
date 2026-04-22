"""Forge POC - Initialize Knowledge Base with Sample Data"""

import asyncio
import logging
from forge.knowledge_base.store import KnowledgeStore
from forge.models import PackageJob, PackageStatus, InstallerMetadata, InstallerType, AIAnalysisResult
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Sample data for common applications
SAMPLE_PACKAGES = [
    {
        "filename": "7z2301-x64.msi",
        "product_name": "7-Zip",
        "manufacturer": "Igor Pavlov",
        "version": "23.01",
        "installer_type": InstallerType.MSI,
        "switches": ["/qn", "/norestart"],
        "install_cmd": 'msiexec /i "7z2301-x64.msi" /qn /norestart',
        "confidence": 0.95,
        "reasoning": "Standard MSI installer from 7-Zip. Well-documented silent switches.",
    },
    {
        "filename": "VSCodeSetup-x64-1.85.exe",
        "product_name": "Visual Studio Code",
        "manufacturer": "Microsoft",
        "version": "1.85",
        "installer_type": InstallerType.EXE,
        "switches": ["/VERYSILENT", "/NORESTART", "/MERGETASKS=!runcode"],
        "install_cmd": '"VSCodeSetup-x64-1.85.exe" /VERYSILENT /NORESTART /MERGETASKS=!runcode',
        "confidence": 0.90,
        "reasoning": "Inno Setup installer. Uses standard Inno Setup silent switches.",
    },
    {
        "filename": "GoogleChromeStandaloneEnterprise64.msi",
        "product_name": "Google Chrome",
        "manufacturer": "Google LLC",
        "version": "120.0",
        "installer_type": InstallerType.MSI,
        "switches": ["/qn", "/norestart", "ALLUSERS=1"],
        "install_cmd": 'msiexec /i "GoogleChromeStandaloneEnterprise64.msi" /qn /norestart ALLUSERS=1',
        "confidence": 0.95,
        "reasoning": "Enterprise MSI from Google. Standard deployment package.",
    },
    {
        "filename": "npp.8.6.Installer.x64.exe",
        "product_name": "Notepad++",
        "manufacturer": "Don Ho",
        "version": "8.6",
        "installer_type": InstallerType.EXE,
        "switches": ["/S"],
        "install_cmd": '"npp.8.6.Installer.x64.exe" /S',
        "confidence": 0.90,
        "reasoning": "NSIS installer. Uses simple /S for silent mode.",
    },
    {
        "filename": "Firefox Setup 121.0.msi",
        "product_name": "Mozilla Firefox",
        "manufacturer": "Mozilla",
        "version": "121.0",
        "installer_type": InstallerType.MSI,
        "switches": ["/qn", "DESKTOP_SHORTCUT=false", "TASKBAR_SHORTCUT=false"],
        "install_cmd": 'msiexec /i "Firefox Setup 121.0.msi" /qn DESKTOP_SHORTCUT=false TASKBAR_SHORTCUT=false',
        "confidence": 0.92,
        "reasoning": "Mozilla MSI package with enterprise customization options.",
    },
    {
        "filename": "vlc-3.0.20-win64.exe",
        "product_name": "VLC Media Player",
        "manufacturer": "VideoLAN",
        "version": "3.0.20",
        "installer_type": InstallerType.EXE,
        "switches": ["/S", "/L=1033"],
        "install_cmd": '"vlc-3.0.20-win64.exe" /S /L=1033',
        "confidence": 0.88,
        "reasoning": "NSIS installer. Language code 1033 = English.",
    },
    {
        "filename": "AcroRdrDC2300620360_en_US.exe",
        "product_name": "Adobe Acrobat Reader DC",
        "manufacturer": "Adobe",
        "version": "23.006.20360",
        "installer_type": InstallerType.EXE,
        "switches": ["/sAll", "/rs", "/msi", "EULA_ACCEPT=YES"],
        "install_cmd": '"AcroRdrDC2300620360_en_US.exe" /sAll /rs /msi EULA_ACCEPT=YES',
        "confidence": 0.85,
        "reasoning": "Adobe bootstrapper with MSI. Requires EULA acceptance.",
        "issues": ["May require Adobe account for updates", "Large download size"],
    },
    {
        "filename": "Zoom_v5.17.msi",
        "product_name": "Zoom",
        "manufacturer": "Zoom Video Communications",
        "version": "5.17",
        "installer_type": InstallerType.MSI,
        "switches": ["/qn", "/norestart", "ZoomAutoUpdate=disabled"],
        "install_cmd": 'msiexec /i "Zoom_v5.17.msi" /qn /norestart ZoomAutoUpdate=disabled',
        "confidence": 0.90,
        "reasoning": "Zoom enterprise MSI. Can disable auto-update via property.",
    },
]


async def main():
    """Initialize knowledge base with sample data."""
    
    logger.info("Initializing knowledge base with sample data...")
    store = KnowledgeStore()
    
    for pkg in SAMPLE_PACKAGES:
        job = PackageJob(
            id=f"sample_{pkg['filename'][:8]}",
            filename=pkg["filename"],
            status=PackageStatus.COMPLETED,
            metadata=InstallerMetadata(
                filename=pkg["filename"],
                file_size=0,
                installer_type=pkg["installer_type"],
                product_name=pkg["product_name"],
                manufacturer=pkg["manufacturer"],
                product_version=pkg["version"],
                file_hash="sample_hash",
            ),
            analysis=AIAnalysisResult(
                silent_switches=pkg["switches"],
                install_command=pkg["install_cmd"],
                uninstall_command="See Add/Remove Programs",
                confidence=pkg["confidence"],
                reasoning=pkg["reasoning"],
                known_issues=pkg.get("issues", []),
            ),
        )
        
        await store.store_package(job)
        logger.info(f"  Added: {pkg['product_name']}")
    
    stats = await store.get_stats()
    logger.info(f"Knowledge base initialized: {stats['total_packages']} packages")


if __name__ == "__main__":
    asyncio.run(main())
