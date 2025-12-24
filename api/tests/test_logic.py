import json
from app.crud import format_records


def test_format_records_with_invalid_geometry():
    """ Tests if the formatter skip logs with corrupted geometry"""
    class MockRecord:
        def __init__(self):
            self.imovel_code = "123"
            self.geometry = "{invalid_json"  # Corrupted Geometry

        def _asdict(self):
            return vars(self)

    results = [MockRecord()]
    formatted = format_records(results)

    # It must return empty list then the parser error was handled
    assert len(formatted) == 0


def test_format_records_success():
    """ Tests if the formatter converts a valid log correctly"""
    class MockRecord:
        def __init__(self):
            self.imovel_code = "456"
            # Valid GEOJSON mock coming from the PostGIS
            self.geometry = json.dumps({
                "type": "Point",
                "coordinates": [-51.0, -21.0]
            })

        def _asdict(self):
            return vars(self)

    results = [MockRecord()]
    formatted = format_records(results)

    # It must contain 1 item and have the expected formatted
    assert len(formatted) == 1
    assert formatted[0]["imovel_code"] == "456"
    assert formatted[0]["geometry"]["type"] == "Point"
