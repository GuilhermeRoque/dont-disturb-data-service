"""create_table_users

Revision ID: 36e9870c84a0
Revises: 
Create Date: 2023-04-23 10:50:01.442548

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '36e9870c84a0'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
	    cpf VARCHAR (45) NOT NULL UNIQUE,
	    email VARCHAR (255) NOT NULL UNIQUE,
	    name VARCHAR (255),
	    provider VARCHAR (255),
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)

    op.execute("""
    CREATE TABLE phones (
        id SERIAL PRIMARY KEY,
        phone VARCHAR(45) NOT NULL UNIQUE ,
        id_user INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
    );
    """)

def downgrade():
    op.execute("DROP TABLE IF EXISTS phones")
    op.execute("DROP TABLE IF EXISTS users")
