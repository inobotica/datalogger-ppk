import sqlalchemy as sa
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Table)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, registry, relationship
from sqlalchemy.sql import func

Base = declarative_base()
mapper_registry = registry()

datalogs_table = Table(
    "datalogs",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("start", DateTime(timezone=True), server_default=func.utcnow()),
    Column("end", DateTime(timezone=True), onupdate=func.utcnow()),
    Column("filename", String),
    Column("state", Boolean, server_default=sa.sql.true()),
)


class Datalogs:
    pass


mapper_registry.map_imperatively(Datalogs, datalogs_table)
