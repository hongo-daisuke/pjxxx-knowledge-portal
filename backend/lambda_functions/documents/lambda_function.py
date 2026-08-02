from __future__ import annotations

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

from config.settings import settings
from handlers.documents_handler import router

logger = Logger(level=settings.log_level)
metrics = Metrics(namespace="KnowledgePortal", service="documents")
app = APIGatewayRestResolver()
app.include_router(router)


@logger.inject_lambda_context(correlation_id_path="requestContext.requestId")
@metrics.log_metrics
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
