"""Handler for routing internal localstack resources"""
import logging

from werkzeug.exceptions import NotFound

from localstack import constants
from localstack.http import Response
from localstack.services.internal import LocalstackResources

from ..api import RequestContext
from ..chain import Handler, HandlerChain

LOG = logging.getLogger(__name__)


class LocalstackResourceHandler(Handler):
    """
    Adapter to serve LocalstackResources as a Handler.
    """

    resources: LocalstackResources

    def __init__(self, resources: LocalstackResources = None) -> None:
        from localstack.services.internal import get_internal_apis

        self.resources = resources or get_internal_apis()

    def __call__(self, chain: HandlerChain, context: RequestContext, response: Response):
        try:
            # serve
            response.update_from(self.resources.dispatch(context.request))
            chain.stop()
        except NotFound:
            path = context.request.path
            if path.startswith(constants.INTERNAL_RESOURCE_PATH + "/"):
                # only return 404 if we're accessing an internal resource, otherwise fall back to the other handlers
                LOG.warning("Unable to find resource handler for path: %s", path)
                chain.respond(404)
