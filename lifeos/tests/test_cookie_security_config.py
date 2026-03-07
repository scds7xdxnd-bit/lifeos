from lifeos.config import DevelopmentConfig, ProductionConfig, StagingConfig, TestingConfig


def test_development_cookie_security_defaults():
    assert DevelopmentConfig.SESSION_COOKIE_SECURE is False
    assert DevelopmentConfig.SESSION_COOKIE_HTTPONLY is True
    assert DevelopmentConfig.SESSION_COOKIE_SAMESITE == "Lax"
    assert DevelopmentConfig.JWT_COOKIE_SECURE is False


def test_testing_cookie_security_defaults():
    assert TestingConfig.SESSION_COOKIE_SECURE is False
    assert TestingConfig.SESSION_COOKIE_HTTPONLY is True
    assert TestingConfig.SESSION_COOKIE_SAMESITE == "Lax"
    assert TestingConfig.JWT_COOKIE_SECURE is False


def test_production_cookie_security_defaults():
    assert ProductionConfig.SESSION_COOKIE_SECURE is True
    assert ProductionConfig.SESSION_COOKIE_HTTPONLY is True
    assert ProductionConfig.SESSION_COOKIE_SAMESITE == "Lax"
    assert ProductionConfig.JWT_COOKIE_SECURE is True


def test_staging_cookie_security_defaults():
    assert StagingConfig.SESSION_COOKIE_SECURE is True
    assert StagingConfig.SESSION_COOKIE_HTTPONLY is True
    assert StagingConfig.SESSION_COOKIE_SAMESITE == "Lax"
    assert StagingConfig.JWT_COOKIE_SECURE is True
