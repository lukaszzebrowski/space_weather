import pandas as pd
import pytest
from app.plot import DataPlot

def test_create_solarwind_table_formatting():
    sample = [(1, "2025-01-13T10:15:00", 431.7, 11.97, 155651)]
    df = DataPlot.create_solarwind_table(sample)

    expected_cols = [
        "Znacznik czasu",
        "Prędkość protonów [km/s]",
        "Gęstość protonów [cm³]",
        "Temperatura protonów [K]"
    ]
    assert list(df.columns) == expected_cols

    assert df.iloc[0]["Prędkość protonów [km/s]"] == "431.70"

    assert df.iloc[0]["Gęstość protonów [cm³]"] == "11.97"

    temp_str = df.iloc[0]["Temperatura protonów [K]"]
    assert "e" in temp_str.lower()

    assert df.iloc[0]["Znacznik czasu"] == "13-01-2025 10:15"
