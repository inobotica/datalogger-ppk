from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship, backref, registry
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import sqlalchemy as sa

Base = declarative_base()
mapper_registry = registry()

datalogs_table = Table(
    "datalogs",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("start", DateTime(timezone=False), server_default=func.utcnow()),
    Column("end", DateTime(timezone=True), onupdate=func.utcnow()),
    Column("state", Boolean, server_default=sa.sql.true())
)

class Datalogs:
    pass
mapper_registry.map_imperatively(Datalogs, datalogs_table)