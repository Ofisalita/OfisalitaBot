import sqlite3

import sqlalchemy as sql
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import registry, declarative_base, Session

import config.db
from config.logger import logger

Base = declarative_base()


class DataBaseDriver:
    """
    Basic driver for the bot database.
    """
    _registry: registry
    _engine: Engine
    _conn: Connection
    _metadata: sql.MetaData

    def __init__(self) -> None:
        """
        Connects to SQLite database and creates tables if they don't exist
        """
        self._registry = registry()

        self._engine = sql.create_engine(f"sqlite+pysqlite:///{config.db.db_file_path}", echo=True, future=True)
        Base.metadata.create_all(self._engine)
        self.session = Session(self._engine)

        logger.info("SQLite initialized")


class Acronyms(Base):
    __tablename__ = 'acronyms'

    acronym = sql.Column(sql.String(255), primary_key=True)
    definition = sql.Column(sql.String(255), nullable=False)

    def __repr__(self):
        return f"Acronyms(acronym={self.acronym!r}, definition={self.definition!r}"
