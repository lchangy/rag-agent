# Bootstrap Specification

## Purpose

Establish the initial backend foundation for the RAG Agent project so later tickets can add retrieval, ingestion, and chat capabilities on top of a working service and database baseline.

## Included in This Bootstrap

- FastAPI application with `GET /health`
- Environment-backed settings module
- SQLAlchemy metadata and database URL/session helpers
- Docker Compose stack for API and PostgreSQL 16 + `pgvector`
- Alembic migration path with an initial `vector` extension migration

## Deferred

- Retrieval or chat endpoints
- Document schemas and embedding pipelines
- Authentication and authorization
- Production deployment automation
