"""add document page extraction method"""
revision="0002_page_extraction_method"; down_revision="0001_initial"; branch_labels=None; depends_on=None
from alembic import op
import sqlalchemy as sa
def upgrade():
    with op.batch_alter_table("document_pages") as batch:
        batch.add_column(sa.Column("extraction_method",sa.String(length=30),nullable=False,server_default="native_pdf"))
def downgrade():
    with op.batch_alter_table("document_pages") as batch: batch.drop_column("extraction_method")
