import sqlite3

class DBManager:
    def __init__(self, db_name="space_weather.db"):
        self.db_name = db_name
        self._create_tables()

    def _create_tables(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Tabela X-Ray
        c.execute('''
            CREATE TABLE IF NOT EXISTS xray (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time_tag TEXT NOT NULL,
                satellite INTEGER,
                current_class TEXT,
                current_ratio REAL,
                current_int_xrlong REAL,
                begin_time TEXT
            )
        ''')

        # Tabela wiatru słonecznego
        c.execute('''
            CREATE TABLE IF NOT EXISTS solarwind (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time_tag TEXT NOT NULL,
                proton_speed REAL,
                proton_density REAL,
                proton_temperature INTEGER
            )
        ''')

        conn.commit()
        conn.close()

    # ------------------ XRAY ------------------
    def insert_xray(self, time_tag, satellite, current_class, current_ratio, current_int_xrlong, begin_time):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            INSERT INTO xray
            (time_tag, satellite, current_class, current_ratio, current_int_xrlong, begin_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (time_tag, satellite, current_class, current_ratio, current_int_xrlong, begin_time))
        conn.commit()
        conn.close()

    def check_xray_exists(self, time_tag):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT 1 FROM xray WHERE time_tag = ?", (time_tag,))
        row = c.fetchone()
        conn.close()
        return (row is not None)

    def get_recent_xray(self, limit=5):
        """
        Zwraca ostatnie `limit` wpisów z xray, posortowane malejąco (najnowsze na górze).
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            SELECT id, time_tag, satellite, current_class, current_ratio, current_int_xrlong, begin_time
            FROM xray
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = c.fetchall()
        conn.close()
        return rows

    # ------------------ SOLAR WIND ------------------
    def insert_solarwind(self, time_tag, proton_speed, proton_density, proton_temperature):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            INSERT INTO solarwind (time_tag, proton_speed, proton_density, proton_temperature)
            VALUES (?, ?, ?, ?)
        """, (time_tag, proton_speed, proton_density, proton_temperature))
        conn.commit()
        conn.close()

    def check_solarwind_exists(self, time_tag):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT 1 FROM solarwind WHERE time_tag = ?", (time_tag,))
        row = c.fetchone()
        conn.close()
        return (row is not None)

    def get_recent_solarwind(self, limit):
        """
        Zwraca ostatnie `limit` wpisów z wiatru słonecznego, malejąco po id.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        if limit is None:  # Jeśli limit jest None, pobierz wszystko
            c.execute("""
                SELECT id, time_tag, proton_speed, proton_density, proton_temperature
                FROM solarwind
                ORDER BY id DESC
            """)
        else:  # Jeśli limit jest ustawiony, ogranicz wyniki
            c.execute("""
                SELECT id, time_tag, proton_speed, proton_density, proton_temperature
                FROM solarwind
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
        rows = c.fetchall()
        conn.close()
        return rows

    def get_latest_solarwind(self):
        """
        Zwraca najnowszy wiersz z wiatru słonecznego (1 pomiar), lub None jeśli brak.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            SELECT id, time_tag, proton_speed, proton_density, proton_temperature
            FROM solarwind
            ORDER BY id DESC
            LIMIT 1
        """)
        row = c.fetchone()
        conn.close()
        return row
