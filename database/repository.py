from models import Datalogs, datalogs_table
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker


class Database:
    def __init__(self) -> None:
        self.engine = create_engine(
            f"sqlite:////home/pi/datalogger-ppk/database/datalogger.db"
        )
        self.session_maker = sessionmaker()
        self.session_maker.configure(bind=self.engine)
        self.session = self.session_maker()

    def insert_log(self):
        self.session.add(Datalogs(state=False))
        self.session.commit()

    def get_log(self, orm_model, condition):
        # query for ``User`` objects
        statement = select(orm_model).filter_by(name=condition)

        # list of ``User`` objects
        user_obj = self.session.scalars(statement).all()

        # query for individual columns
        statement = select(orm_model.name, orm_model.fullname)

        # list of Row objects
        rows = self.session.execute(statement).all()

    def test_connection(self):
        statement = self.session.execute(select(Datalogs))

        res = statement.scalars().all()
        for row in res:
            print(row.start, row.end)


if __name__ == "__main__":
    print("starting database")
    database = Database()
    database.test_connection()
