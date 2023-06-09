"""create_view_users_active

Revision ID: 0d20c35bac25
Revises: 36e9870c84a0
Create Date: 2023-04-23 10:54:29.514685

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '0d20c35bac25'
down_revision = '36e9870c84a0'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE VIEW users_active AS SELECT users.cpf, users.email, users.name, phones.phone FROM users INNER JOIN phones ON phones.id_user = users.id WHERE phones.created_at > NOW() - INTERVAL '180 days';")


def downgrade():
    op.execute("DROP VIEW IF EXISTS users_active")
