"""initial schema

Revision ID: 0001_initial
"""
revision="0001_initial"; down_revision=None; branch_labels=None; depends_on=None
from alembic import op
from app.db import Base
from app import models
def upgrade(): Base.metadata.create_all(op.get_bind())
def downgrade(): Base.metadata.drop_all(op.get_bind())
