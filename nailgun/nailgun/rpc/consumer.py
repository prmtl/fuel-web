# -*- coding: utf-8 -*-

#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import amqp.exceptions as amqp_exceptions
from kombu.mixins import ConsumerMixin
import six


from nailgun import rpc
from nailgun.db import db
from nailgun.errors import errors
from nailgun.logger import logger
from nailgun.rpc import utils as rpc_utils


class RPCConsumer(ConsumerMixin):

    def __init__(self, connection, receiver):
        self.connection = connection
        self.receiver = receiver

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[rpc.nailgun_queue],
                         callbacks=[self.consume_msg])]

    def consume_msg(self, body, msg):
        callback = getattr(self.receiver, body["method"])
        try:
            callback(**body["args"])
        except errors.CannotFindTask as e:
            logger.warn(str(e))
            msg.ack()
        except Exception:
            logger.exception('Unknown exception during callback call')
            msg.ack()
        except KeyboardInterrupt:
            logger.error("Receiverd interrupted.")
            msg.requeue()
            raise
        else:
            db.commit()
            msg.ack()
        finally:
            db.remove()

    def on_precondition_failed(self, error_msg):
        logger.warning(error_msg)
        rpc_utils.delete_entities(
            self.connection, rpc.nailgun_exchange, rpc.nailgun_queue)

    def run(self, *args, **kwargs):
        try:
            super(RPCConsumer, self).run(*args, **kwargs)
        except amqp_exceptions.PreconditionFailed as e:
            self.on_precondition_failed(six.text_type(e))
            self.run(*args, **kwargs)
