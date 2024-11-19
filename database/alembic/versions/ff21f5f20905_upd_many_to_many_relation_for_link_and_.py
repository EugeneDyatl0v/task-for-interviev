"""upd many-to-many relation for link and collection

Revision ID: ff21f5f20905
Revises: 20906028dfa4
Create Date: 2024-11-19 00:35:11.392494

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff21f5f20905'
down_revision: Union[str, None] = '20906028dfa4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('link_vault_link_collection_associations',
    sa.Column('id', sa.UUID(), nullable=False, comment='Unique identifier for the collection'),
    sa.Column('link_id', sa.UUID(), nullable=False, comment='Identifier of the user who owns the collection'),
    sa.Column('collection_id', sa.UUID(), nullable=False, comment='Identifier of the user who owns the collection'),
    sa.ForeignKeyConstraint(['collection_id'], ['link_vault_collections.id'], ),
    sa.ForeignKeyConstraint(['link_id'], ['link_vault_links.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('link_id', 'collection_id', name='uq_link_collection')
    )
    op.drop_constraint('link_vault_links_collection_id_fkey', 'link_vault_links', type_='foreignkey')
    op.drop_column('link_vault_links', 'collection_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('link_vault_links', sa.Column('collection_id', sa.UUID(), autoincrement=False, nullable=True, comment='Identifier of the collection associated with the link'))
    op.create_foreign_key('link_vault_links_collection_id_fkey', 'link_vault_links', 'link_vault_collections', ['collection_id'], ['id'])
    op.drop_table('link_vault_link_collection_associations')
    # ### end Alembic commands ###
