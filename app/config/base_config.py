""" Base configuration for the application. """

from os import getenv, getcwd, path
from datetime import timedelta


class BaseConfig:  # pylint: disable=too-few-public-methods
    """Base configuration."""

    SECRET_KEY = getenv("SECRET_KEY")
    JWT_SECRET_KEY = getenv("JWT_SECRET_KEY")
    ENCRYPTION_KEY = getenv("ENCRYPTION_KEY", "")

    JWT_ALGORITHM = "HS256"
    JWT_DECODE_ALGORITHMS = ["HS256"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)

    API_TITLE = "EZ-Parking API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"

    MAIL_SERVER = getenv("MAIL_SERVER")
    MAIL_PORT = getenv("MAIL_PORT")
    MAIL_USE_TLS = getenv("MAIL_USE_TLS")
    MAIL_USERNAME = getenv("MAIL_USERNAME")
    MAIL_PASSWORD = getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = getenv("MAIL_DEFAULT_SENDER")

    JWT_ACCESS_COOKIE_NAME = "Authorization"
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_COOKIE_SECURE = True
    JWT_SESSION_COOKIE = False
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_DOMAIN = "localhost"
    JWT_COOKIE_SAMESITE = "None"
    JWT_CSRF_CHECK_FORM = False
    JWT_CSRF_IN_COOKIES = True
    JWT_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]
    JWT_ACCESS_CSRF_HEADER_NAME = "X-CSRF-TOKEN"
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_REFRESH_CSRF_HEADER_NAME = "X-CSRF-TOKEN"
    JWT_ACCESS_CSRF_COOKIE_NAME = "X-CSRF-TOKEN"

    LOGGING_LEVEL = "INFO"
    LOGGING_PATH = path.join(getcwd(), "logs", "authentication.log")
    IS_PRODUCTION = getenv("ENVIRONMENT", "") == "production"

    DEVELOPMENT_URL = getenv("DEVELOPMENT_URL", "http://localhost:5000")
    PRODUCTION_URL = getenv("PRODUCTION_URL", "")
