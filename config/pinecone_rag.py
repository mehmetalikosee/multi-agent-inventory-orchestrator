"""
Pinecone RAG configuration stub for business documents and inventory logs.

In production: embed documents (policies, inventory logs), store in Pinecone,
and use a retrieval tool so agents can query this knowledge base.
"""

import logging
from typing import Optional

from config import get_settings

logger = logging.getLogger(__name__)


def get_pinecone_index():
    """
    Return a Pinecone index client if configured; otherwise None.
    Used for RAG over business documents and inventory logs.
    """
    settings = get_settings()
    if not settings.pinecone_api_key:
        logger.debug("Pinecone not configured; RAG disabled")
        return None
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=settings.pinecone_api_key)
        return pc.Index(settings.pinecone_index_name)
    except Exception as e:
        logger.warning("Could not connect to Pinecone: %s", e)
        return None


def query_documents(query: str, top_k: int = 5) -> list[dict]:
    """
    Placeholder: query vector store for relevant business documents.
    Returns empty list until Pinecone index is populated and connected.
    """
    index = get_pinecone_index()
    if index is None:
        return []
    # TODO: embed query, index.query(...), return matches
    return []
