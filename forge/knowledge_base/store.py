"""Forge POC - Knowledge Base with ChromaDB"""

import logging
from datetime import datetime
from typing import Optional
import json

import chromadb

from forge.config import settings
from forge.models import PackageJob

logger = logging.getLogger(__name__)


class KnowledgeStore:
    """Knowledge base for storing and retrieving packaging information."""
    
    def __init__(self):
        """Initialize ChromaDB client and collections."""
        # Use the new persistent client API
        self.client = chromadb.PersistentClient(
            path=str(settings.chroma_persist_dir)
        )
        
        # Collection for successful packages
        self.packages = self.client.get_or_create_collection(
            name="packages",
            metadata={"description": "Successfully packaged applications"}
        )
        
        # Collection for install commands and switches
        self.commands = self.client.get_or_create_collection(
            name="commands",
            metadata={"description": "Install commands and switches"}
        )
        
        logger.info(f"Knowledge base initialized with {self.packages.count()} packages")
    
    async def store_package(self, job: PackageJob) -> None:
        """Store a completed package job in the knowledge base."""
        
        if not job.metadata or not job.analysis:
            logger.warning(f"Cannot store incomplete job: {job.id}")
            return
        
        # Create document text for embedding
        doc_text = self._create_document_text(job)
        
        # Create metadata
        metadata = {
            "job_id": job.id,
            "filename": job.filename,
            "product_name": job.metadata.product_name or "",
            "manufacturer": job.metadata.manufacturer or "",
            "version": job.metadata.product_version or "",
            "installer_type": job.metadata.installer_type.value,
            "confidence": job.analysis.confidence,
            "install_command": job.analysis.install_command,
            "stored_at": datetime.utcnow().isoformat(),
        }
        
        # Store in packages collection
        self.packages.add(
            documents=[doc_text],
            metadatas=[metadata],
            ids=[job.id],
        )
        
        # Store switches/commands separately for better retrieval
        switches_text = " ".join(job.analysis.silent_switches)
        self.commands.add(
            documents=[f"{job.filename} {switches_text} {job.analysis.install_command}"],
            metadatas={
                "job_id": job.id,
                "filename": job.filename,
                "switches": json.dumps(job.analysis.silent_switches),
            },
            ids=[f"{job.id}_cmd"],
        )
        
        logger.info(f"Stored package {job.id} ({job.filename}) in knowledge base")
    
    async def find_similar(
        self, 
        filename: str, 
        metadata: Optional[any] = None,
        limit: int = 5
    ) -> list[dict]:
        """Find similar packages in the knowledge base."""
        
        # Build query text
        query_parts = [filename]
        if metadata:
            if hasattr(metadata, 'product_name') and metadata.product_name:
                query_parts.append(metadata.product_name)
            if hasattr(metadata, 'manufacturer') and metadata.manufacturer:
                query_parts.append(metadata.manufacturer)
        
        query_text = " ".join(query_parts)
        
        try:
            results = self.packages.query(
                query_texts=[query_text],
                n_results=limit,
            )
            
            if not results or not results['metadatas']:
                return []
            
            # Format results
            similar = []
            for i, meta in enumerate(results['metadatas'][0]):
                similar.append({
                    "filename": meta.get("filename", ""),
                    "product_name": meta.get("product_name", ""),
                    "install_command": meta.get("install_command", ""),
                    "confidence": meta.get("confidence", 0),
                    "distance": results['distances'][0][i] if results.get('distances') else None,
                })
            
            return similar
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    async def search(self, query: str, limit: int = 5) -> list[dict]:
        """Search the knowledge base with a text query."""
        
        try:
            results = self.packages.query(
                query_texts=[query],
                n_results=limit,
            )
            
            if not results or not results['metadatas']:
                return []
            
            # Format results
            found = []
            for i, meta in enumerate(results['metadatas'][0]):
                found.append({
                    "job_id": meta.get("job_id", ""),
                    "filename": meta.get("filename", ""),
                    "product_name": meta.get("product_name", ""),
                    "manufacturer": meta.get("manufacturer", ""),
                    "version": meta.get("version", ""),
                    "install_command": meta.get("install_command", ""),
                    "confidence": meta.get("confidence", 0),
                })
            
            return found
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    async def get_stats(self) -> dict:
        """Get statistics about the knowledge base."""
        return {
            "total_packages": self.packages.count(),
            "total_commands": self.commands.count(),
            "persist_directory": str(settings.chroma_persist_dir),
        }
    
    def _create_document_text(self, job: PackageJob) -> str:
        """Create a rich text document for embedding."""
        
        parts = [
            f"Filename: {job.filename}",
            f"Product: {job.metadata.product_name or 'Unknown'}",
            f"Manufacturer: {job.metadata.manufacturer or 'Unknown'}",
            f"Version: {job.metadata.product_version or 'Unknown'}",
            f"Type: {job.metadata.installer_type.value}",
            f"Switches: {' '.join(job.analysis.silent_switches)}",
            f"Install: {job.analysis.install_command}",
            f"Notes: {job.analysis.reasoning}",
        ]
        
        if job.analysis.known_issues:
            parts.append(f"Issues: {', '.join(job.analysis.known_issues)}")
        
        return "\n".join(parts)
