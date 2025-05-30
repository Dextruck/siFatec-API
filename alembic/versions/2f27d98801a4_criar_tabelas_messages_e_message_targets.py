"""Criar tabelas messages e message_targets

Revision ID: [SERÁ_GERADO_AUTOMATICAMENTE]
Revises: fbbf3b539a23
Create Date: [DATA_ATUAL]

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '[SERÁ_GERADO_AUTOMATICAMENTE]'
down_revision: Union[str, None] = 'fbbf3b539a23'  # Sua migração anterior
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # Criar tabela messages
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('send_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),  # Do AuditMixin
        sa.Column('updated_at', sa.DateTime(), nullable=True),  # Do AuditMixin
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar tabela message_targets
    op.create_table(
        'message_targets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('class_group_id', sa.Integer(), nullable=True),
        sa.Column('course_id', sa.Integer(), nullable=True),
        sa.Column('institution_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),  # Do AuditMixin
        sa.Column('updated_at', sa.DateTime(), nullable=True),  # Do AuditMixin
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['class_group_id'], ['class_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='CASCADE')
    )
    
    # Criar índices para melhor performance nas consultas
    op.create_index('ix_messages_send_at', 'messages', ['send_at'])
    op.create_index('ix_messages_expires_at', 'messages', ['expires_at'])
    op.create_index('ix_message_targets_message_id', 'message_targets', ['message_id'])
    op.create_index('ix_message_targets_class_group_id', 'message_targets', ['class_group_id'])
    op.create_index('ix_message_targets_course_id', 'message_targets', ['course_id'])
    op.create_index('ix_message_targets_institution_id', 'message_targets', ['institution_id'])


def downgrade() -> None:
    """Downgrade schema."""
    
    # Remover índices
    op.drop_index('ix_message_targets_institution_id', table_name='message_targets')
    op.drop_index('ix_message_targets_course_id', table_name='message_targets')
    op.drop_index('ix_message_targets_class_group_id', table_name='message_targets')
    op.drop_index('ix_message_targets_message_id', table_name='message_targets')
    op.drop_index('ix_messages_expires_at', table_name='messages')
    op.drop_index('ix_messages_send_at', table_name='messages')
    
    # Remover tabelas (ordem inversa da criação)
    op.drop_table('message_targets')
    op.drop_table('messages')