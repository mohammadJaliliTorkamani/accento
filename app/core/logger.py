import logging
from logging.handlers import RotatingFileHandler

# Logger configuration
logger = logging.getLogger("accento")
logger.setLevel(logging.INFO)

# Rotating file handler (keeps logs manageable)
handler = RotatingFileHandler("app.log", maxBytes=5 * 1024 * 1024, backupCount=2)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)
