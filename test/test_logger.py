import logging
from unittest.mock import patch
from fastcrawler.logger.adopter import ERROR, WARNING, INFO, DEBUG


def test_logger_info(logger):
    with patch.object(logging.Logger, "_log") as mock_log:
        logger.info("Test info message")
        mock_log.assert_called_with(INFO, "Test info message", args=())


def test_logger_debug(logger):
    with patch.object(logging.Logger, "_log") as mock_log:
        logger.debug("Test debug message")
        mock_log.assert_called_with(DEBUG, "Test debug message", args=())


def test_logger_error(logger):
    with patch.object(logging.Logger, "_log") as mock_log:
        logger.error("Test error message")
        mock_log.assert_called_with(ERROR, "Test error message", args=())


def test_logger_warning(logger):
    with patch.object(logging.Logger, "_log") as mock_log:
        logger.warning("Test warning message")
        mock_log.assert_called_with(WARNING, "Test warning message", args=())


def test_add_custom_handler(logger):
    custom_handler = logging.StreamHandler()
    logger.add_handler(custom_handler)

    assert custom_handler in logger._logger.handlers


def test_custom_handler_formatting(logger):
    custom_handler = logging.StreamHandler()
    custom_format = "%(levelname)s - %(message)s"
    logger.add_handler(custom_handler, formatter=custom_format)

    with patch.object(logging.Handler, "emit") as mock_emit:
        logger.info("Custom handler test")
        mock_emit.assert_called_with(
            logging.LogRecord(
                name="FastCrawler",
                level=INFO,
                pathname=None,
                lineno=None,
                msg="INFO - Custom handler test",
                args=(),
                exc_info=None,
            )
        )
