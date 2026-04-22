"""Forge POC - Pydantic Models"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PackageStatus(str, Enum):
    """Status of a package job."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    PACKAGING = "packaging"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class InstallerType(str, Enum):
    """Supported installer types."""
    MSI = "msi"
    EXE = "exe"
    MSIX = "msix"
    UNKNOWN = "unknown"


class InstallerMetadata(BaseModel):
    """Extracted metadata from an installer."""
    filename: str
    file_size: int
    installer_type: InstallerType
    product_name: Optional[str] = None
    product_version: Optional[str] = None
    manufacturer: Optional[str] = None
    detected_switches: list[str] = Field(default_factory=list)
    file_hash: str = ""


class AIAnalysisResult(BaseModel):
    """Result from AI analysis of an installer."""
    silent_switches: list[str] = Field(default_factory=list)
    install_command: str = ""
    uninstall_command: str = ""
    confidence: float = 0.0
    reasoning: str = ""
    known_issues: list[str] = Field(default_factory=list)
    similar_packages: list[str] = Field(default_factory=list)


class WDACPolicy(BaseModel):
    """Generated WDAC policy information."""
    policy_name: str
    policy_xml: str
    rules: list[dict] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class PackageJob(BaseModel):
    """A packaging job request and its status."""
    id: str
    filename: str
    status: PackageStatus = PackageStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Results
    metadata: Optional[InstallerMetadata] = None
    analysis: Optional[AIAnalysisResult] = None
    policy: Optional[WDACPolicy] = None
    
    # Error tracking
    error_message: Optional[str] = None


class PackageJobCreate(BaseModel):
    """Request to create a new package job."""
    filename: str


class PackageJobResponse(BaseModel):
    """Response for a package job."""
    id: str
    filename: str
    status: PackageStatus
    created_at: datetime
    metadata: Optional[InstallerMetadata] = None
    analysis: Optional[AIAnalysisResult] = None
    policy: Optional[WDACPolicy] = None
    error_message: Optional[str] = None
