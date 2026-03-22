"""Add chunks and embeddings tables."""

from alembic import op
import sqlalchemy as sa

from core.embeddings import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL
from core.models import VectorType

# revision identifiers, used by Alembic.
revision = "0002_add_chunks_and_embeddings"
down_revision = "0001_enable_pgvector"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chunks",
        sa.Column("id", sa.Uuid(as_uuid=False), primary_key=True, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "embeddings",
        sa.Column("chunk_id", sa.Uuid(as_uuid=False), nullable=False),
        sa.Column("embedding", VectorType(EMBEDDING_DIMENSIONS), nullable=False),
        sa.Column(
            "model",
            sa.Text(),
            nullable=False,
            server_default=sa.text(f"'{EMBEDDING_MODEL}'"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["chunk_id"], ["chunks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("chunk_id"),
    )


def downgrade() -> None:
    op.drop_table("embeddings")
    op.drop_table("chunks")
