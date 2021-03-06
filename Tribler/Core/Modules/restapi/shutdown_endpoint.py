import os
import json
import logging

from twisted.web import resource
from twisted.internet import reactor

from Tribler.Core.Modules.process_checker import ProcessChecker


class ShutdownEndpoint(resource.Resource):
    """
    With this endpoint you can trigger a Tribler shutdown.
    """

    def __init__(self, session):
        resource.Resource.__init__(self)
        self._logger = logging.getLogger(self.__class__.__name__)
        self.session = session
        self.process_checker = ProcessChecker()

    def render_PUT(self, request):
        """
        .. http:put:: /shutdown

        A PUT request to this endpoint triggers a Tribler shutdown.

            **Example request**:

            .. sourcecode:: none

                curl -X PUT http://localhost:8085/shutdown

            **Example response**:

            .. sourcecode:: javascript

                {
                    "shutdown": True,
                    "gracetime": 2.0
                }
        """
        gracetime = 2.0

        def shutdown_process(_, code=1):
            reactor.addSystemEventTrigger('after', 'shutdown', os._exit, code)
            reactor.stop()
            self.process_checker.remove_lock_file()

        def log_and_shutdown(failure):
            self._logger.error(failure.value)
            shutdown_process(failure, 0)

        self.session.shutdown(gracetime=gracetime).addCallback(shutdown_process).addErrback(log_and_shutdown)

        return json.dumps({"shutdown": True, "gracetime": gracetime})
