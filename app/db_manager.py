import sqlite3
import pandas as pd

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
                begin_time TEXT,
                begin_class TEXT,
                max_time TEXT,
                max_class TEXT,
                max_xrlong REAL,
                end_time TEXT,
                end_class TEXT
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

        # Tabela danych GOES (Primary/Secondary)
        c.execute('''
                   CREATE TABLE IF NOT EXISTS goes_data (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       time_tag TEXT NOT NULL,
                       satellite INTEGER,
                       flux REAL,
                       observed_flux REAL,
                       electron_correction REAL,
                       electron_contamination BOOLEAN,
                       energy TEXT,
                       UNIQUE(time_tag, satellite)  -- Zapobiega duplikatom
                   )
               ''')

        # Tabela do przechowywania obrazów
        c.execute('''
                CREATE TABLE IF NOT EXISTS solar_images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,       -- Nazwa źródła (SOHO C2, SOHO C3, SDO HMI)
                    image BLOB NOT NULL,        -- Obraz w formacie BLOB
                    image_hash TEXT NOT NULL,   -- Hash obrazu
                    time_tag TEXT NOT NULL,     -- Znacznik czasu pobrania
                    UNIQUE(source, image_hash)  -- Zapobiega duplikatom
                )
            ''')

        conn.commit()
        conn.close()

    def insert_xray(self, time_tag, satellite, current_class, current_ratio, current_int_xrlong,
                    begin_time, begin_class, max_time, max_class, max_xrlong, end_time, end_class):
        """Zapisuje dane X-Ray do bazy danych."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            INSERT INTO xray (
                time_tag,
                satellite,
                current_class,
                current_ratio,
                current_int_xrlong,
                begin_time,
                begin_class,
                max_time,
                max_class,
                max_xrlong,
                end_time,
                end_class
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            time_tag,
            satellite,
            current_class,
            current_ratio,
            current_int_xrlong,
            begin_time,
            begin_class,
            max_time,
            max_class,
            max_xrlong,
            end_time,
            end_class
        ))
        conn.commit()
        conn.close()

    def check_xray_exists(self, time_tag):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT 1 FROM xray WHERE time_tag = ?", (time_tag,))
        row = c.fetchone()
        conn.close()
        return (row is not None)

    def get_latest_xray_event(self):
        """Zwraca najnowsze zdarzenie X-Ray ze wszystkimi szczegółami."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            SELECT satellite, current_class, current_ratio, current_int_xrlong, 
                   begin_time, begin_class, max_time, max_class, 
                   max_xrlong, end_time, end_class
            FROM xray
            ORDER BY time_tag DESC
            LIMIT 1
        """)
        row = c.fetchone()
        conn.close()
        return row

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

    def check_goes_data_exists(self, time_tag, satellite):
        """Sprawdza, czy dane GOES z danym time_tag i satelitą już istnieją."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            SELECT 1 FROM goes_data
            WHERE time_tag = ? AND satellite = ?
        """, (time_tag, satellite))
        row = c.fetchone()
        conn.close()
        return row is not None

    def insert_goes_data(self, time_tag, satellite, flux, observed_flux, electron_correction, electron_contamination,
                         energy):
        """Dodaje nowy wpis GOES do bazy danych."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            INSERT OR IGNORE INTO goes_data
            (time_tag, satellite, flux, observed_flux, electron_correction, electron_contamination, energy)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (time_tag, satellite, flux, observed_flux, electron_correction, electron_contamination, energy))
        conn.commit()
        conn.close()

    def get_recent_goes_data(self, limit):
        """Zwraca ostatnie `limit` wpisów z tabeli GOES."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        if limit is None:
            c.execute("""
            SELECT id, time_tag, satellite, flux, observed_flux, electron_correction, electron_contamination, energy
            FROM goes_data
            ORDER BY id DESC
        """)
        else:
            c.execute("""
                SELECT id, time_tag, satellite, flux, observed_flux, electron_correction, electron_contamination, energy
                FROM goes_data
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))

        rows = c.fetchall()
        conn.close()
        return rows

    def get_all_from_table(self, table_name):
        """Zwraca wszystkie dane z wybranej tabeli."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(f"SELECT * FROM {table_name}")
        rows = c.fetchall()
        columns = [description[0] for description in c.description]
        conn.close()
        return rows, columns

    def check_image_exists(self, source, image_hash):
        """Sprawdza, czy obraz o danym hashu już istnieje w bazie."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT 1 FROM solar_images WHERE source = ? AND image_hash = ?", (source, image_hash))
        exists = c.fetchone() is not None
        conn.close()
        return exists

    def insert_solar_image(self, source, image_data, image_hash, time_tag):
        """Zapisuje obraz do bazy danych."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            INSERT INTO solar_images (source, image, image_hash, time_tag)
            VALUES (?, ?, ?, ?)
        """, (source, image_data, image_hash, time_tag))
        conn.commit()
        conn.close()

    def get_latest_solar_images(self):
        """Zwraca najnowsze obrazy z każdego źródła."""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Pobiera najnowszy obraz dla każdego źródła
        c.execute("""
            SELECT source, image, time_tag
            FROM solar_images
            WHERE (source, time_tag) IN (
                SELECT source, MAX(time_tag)
                FROM solar_images
                GROUP BY source
            )
        """)

        images = c.fetchall()
        conn.close()
        return images

    def get_solar_images_for_sources_in_range(self, start_time, end_time, sources):
        """
        Pobiera obrazy w przedziale [start_time, end_time] dla listy źródeł (sources).
        """
        placeholders = ", ".join(["?"] * len(sources))
        sql = f"""
            SELECT source, image, time_tag
            FROM solar_images
            WHERE time_tag >= ?
              AND time_tag <= ?
              AND source IN ({placeholders})
            ORDER BY time_tag ASC
        """
        # Parametry: start_time, end_time, potem rozpakowana lista 'sources'
        params = [start_time, end_time] + list(sources)

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(sql, params)
        rows = c.fetchall()
        conn.close()
        return rows