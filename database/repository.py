import os
import time
from datetime import datetime, timezone

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

from .models import Datalogs, Gis, datalogs_table, gis_table


class Database:
    def __init__(self) -> None:
        self.engine = create_engine(
            f"sqlite:////home/pi/datalogger-ppk/database/datalogger.db"
        )
        self.session_maker = sessionmaker()
        self.session_maker.configure(bind=self.engine)
        self.session = self.session_maker()
        self.use_tow_time = True

    def insert_data(self, db_obj):
        self.session.add(db_obj)
        self.session.commit()

    def insert_log(self):
        self.base_dir = "/home/pi/datalogger-ppk/logs"
        self.filename = (
            datetime.now(timezone.utc).strftime("%y%m%d_%H%M%S") + "_rover.ubx"
        )
        self.filepath = os.path.join(self.base_dir, self.filename)
        db_obj = Datalogs(filename=self.filepath)
        self.insert_data(db_obj)
        return db_obj

    def insert_position(self, state):
        _timestamp = (
            state.tow_time if self.use_tow_time and state.tow_time else time.time()
        )
        _unix_time = _timestamp.timestamp()

        # print("sys time:", datetime.utcnow())
        # print("tow time:", _timestamp)

        gis_obj = Gis(
            unix_time=_unix_time,
            time=_timestamp,
            photo=state.photo.name,
            pitch=state.imu.pitch,
            roll=state.imu.roll,
            datalog_id=state.db_log.id,
        )

        self.insert_data(gis_obj)

    def get_gps_points_cloud(self, filename, is_full_path=False):
        if is_full_path:
            self.filepath = filename
        else:
            self.base_dir = "/home/pi/datalogger-ppk/logs"
            self.filename = filename + ".ubx"
            self.filepath = os.path.join(self.base_dir, self.filename)

        print("Searching in db for: ", self.filepath)
        query = select(Datalogs.id).where(Datalogs.filename == self.filepath)
        result = self.session.scalars(query).all()

        if not result or len(result) < 1:
            return None

        datalog_id = result[0]
        query = select(Gis).where(Gis.datalog_id == datalog_id)
        result = self.session.scalars(query).all()

        return result if result else []

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
