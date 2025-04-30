import pytest
from app.db_manager import DBManager

@pytest.fixture
def db(tmp_path):
    p = tmp_path / "test.db"
    mgr = DBManager(str(p))
    return mgr

def test_insert_and_get_one_solarwind(db):
    ts = "2025-01-13 10:15:00"
    db.insert_solarwind(ts, proton_speed=400.5, proton_density=10.2, proton_temperature=123456)

    rows = db.get_recent_solarwind(limit=1)
    assert len(rows) == 1

    _id, time_tag, speed, density, temp = rows[0]
    assert time_tag == ts
    assert speed == 400.5
    assert density == 10.2
    assert temp == 123456

def test_no_duplicates_on_check_exists(db):
    assert not db.check_solarwind_exists("2025-01-01 00:00:00")

    ts = "2025-01-13 11:00:00"
    db.insert_solarwind(ts, 100, 1.5, 50000)
    assert db.check_solarwind_exists(ts)

    db.insert_solarwind(ts, 200, 2.5, 60000)
    assert db.check_solarwind_exists(ts)
