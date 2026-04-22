"""Forge POC - FastAPI Backend"""

import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiofiles
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from forge.config import settings
from forge.models import (
    PackageJob, PackageJobResponse, PackageStatus,
    InstallerMetadata, InstallerType
)
from forge.services.analyzer import InstallerAnalyzer
from forge.services.packager import Packager
from forge.knowledge_base.store import KnowledgeStore

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Forge POC",
    description="AI-powered endpoint compliance automation",
    version="0.1.0"
)

# CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store (would be Redis/DB in production)
jobs: dict[str, PackageJob] = {}

# Services
analyzer = InstallerAnalyzer()
packager = Packager()
knowledge_store = KnowledgeStore()


def get_installer_type(filename: str) -> InstallerType:
    """Determine installer type from filename."""
    suffix = Path(filename).suffix.lower()
    return {
        ".msi": InstallerType.MSI,
        ".exe": InstallerType.EXE,
        ".msix": InstallerType.MSIX,
    }.get(suffix, InstallerType.UNKNOWN)


async def process_package_job(job_id: str, file_path: Path):
    """Background task to process a packaging job."""
    job = jobs.get(job_id)
    if not job:
        return
    
    try:
        # Step 1: Analyze
        job.status = PackageStatus.ANALYZING
        job.updated_at = datetime.utcnow()
        
        logger.info(f"[{job_id}] Analyzing installer: {job.filename}")
        
        # Extract metadata and AI analysis
        job.metadata = await analyzer.extract_metadata(file_path)
        job.analysis = await analyzer.analyze_installer(file_path, job.metadata)
        
        # Step 2: Check knowledge base for similar packages
        similar = await knowledge_store.find_similar(job.filename, job.metadata)
        if similar:
            job.analysis.similar_packages = [s["filename"] for s in similar[:3]]
            logger.info(f"[{job_id}] Found {len(similar)} similar packages in knowledge base")
        
        # Step 3: Generate package
        job.status = PackageStatus.PACKAGING
        job.updated_at = datetime.utcnow()
        
        logger.info(f"[{job_id}] Generating package...")
        package_result = await packager.create_package(job.metadata, job.analysis)
        
        # Step 4: Generate WDAC policy
        job.status = PackageStatus.VALIDATING
        job.updated_at = datetime.utcnow()
        
        logger.info(f"[{job_id}] Generating WDAC policy...")
        job.policy = await packager.generate_wdac_policy(job.metadata, job.analysis)
        
        # Step 5: Store in knowledge base for future reference
        await knowledge_store.store_package(job)
        
        # Check if needs human review
        if job.analysis.confidence < 0.7:
            job.status = PackageStatus.NEEDS_REVIEW
            logger.warning(f"[{job_id}] Low confidence ({job.analysis.confidence:.0%}), needs review")
        else:
            job.status = PackageStatus.COMPLETED
            logger.info(f"[{job_id}] Completed successfully!")
        
        job.updated_at = datetime.utcnow()
        
    except Exception as e:
        logger.error(f"[{job_id}] Failed: {e}")
        job.status = PackageStatus.FAILED
        job.error_message = str(e)
        job.updated_at = datetime.utcnow()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Forge POC"}


@app.post("/packages/upload", response_model=PackageJobResponse)
async def upload_installer(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload an installer and start the packaging process."""
    
    # Validate file type
    installer_type = get_installer_type(file.filename)
    if installer_type == InstallerType.UNKNOWN:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: .msi, .exe, .msix"
        )
    
    # Generate job ID and save file
    job_id = str(uuid.uuid4())[:8]
    file_path = settings.upload_dir / f"{job_id}_{file.filename}"
    
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    # Create job
    job = PackageJob(
        id=job_id,
        filename=file.filename,
        status=PackageStatus.PENDING
    )
    jobs[job_id] = job
    
    # Start background processing
    background_tasks.add_task(process_package_job, job_id, file_path)
    
    logger.info(f"Created job {job_id} for {file.filename}")
    
    return PackageJobResponse(**job.model_dump())


@app.get("/packages/{job_id}", response_model=PackageJobResponse)
async def get_package_status(job_id: str):
    """Get the status of a packaging job."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return PackageJobResponse(**job.model_dump())


@app.get("/packages", response_model=list[PackageJobResponse])
async def list_packages(status: Optional[PackageStatus] = None):
    """List all packaging jobs, optionally filtered by status."""
    result = list(jobs.values())
    if status:
        result = [j for j in result if j.status == status]
    return [PackageJobResponse(**j.model_dump()) for j in result]


@app.get("/knowledge/stats")
async def knowledge_stats():
    """Get statistics about the knowledge base."""
    return await knowledge_store.get_stats()


@app.get("/knowledge/search")
async def search_knowledge(query: str, limit: int = 5):
    """Search the knowledge base."""
    results = await knowledge_store.search(query, limit)
    return {"query": query, "results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
