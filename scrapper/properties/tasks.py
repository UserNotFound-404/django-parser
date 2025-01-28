from celery import shared_task
from celery.utils.log import get_task_logger

from .scraper import scrape_properties_task


logger = get_task_logger(__name__)


@shared_task
def update_properties():
    logger.info("Starting task")
    scrape_properties_task()
    logger.info("Ending task")
