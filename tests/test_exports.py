import claim_pilot_core


def test_version():
    assert claim_pilot_core.__version__ == "2026.05.1"


def test_public_exports():
    assert hasattr(claim_pilot_core, "get_settings")
    assert hasattr(claim_pilot_core, "get_logger")
    assert hasattr(claim_pilot_core, "setup_logging")
    assert hasattr(claim_pilot_core, "LogContext")
    assert hasattr(claim_pilot_core, "DatabaseConnection")
    assert hasattr(claim_pilot_core, "get_db")
