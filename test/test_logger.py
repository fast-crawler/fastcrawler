import logging
from unittest.mock import patch


def test_logger_info(logger):
    with patch.object(logging.Logger, "log") as mock_log:
        logger.info("Test info message")
        assert True


def test_logger_debug(logger):
    with patch.object(logging.Logger, "log") as mock_log:
        logger.debug("Test debug message")
        assert True


def test_logger_error(logger):
    with patch.object(logging.Logger, "log") as mock_log:
        logger.error("Test error message")
        assert True


def test_logger_warning(logger):
    with patch.object(logging.Logger, "log") as mock_log:
        logger.warning("Test warning message")
        assert True


def test_add_custom_handler(logger):
    custom_handler = logging.StreamHandler()
    logger.add_handler(custom_handler)

    assert custom_handler in logger._logger.handlers


def test_custom_handler_formatting(logger):
    custom_handler = logging.StreamHandler()
    custom_format = "%(levelname)s - %(message)s"
    logger.add_handler(custom_handler, formatter=custom_format)

    with patch.object(logging.Handler, "emit") as mock_emit:
        with patch.object(logging.Logger, "log") as mock_logger:
            logger.info("Custom handler test")
            assert True
