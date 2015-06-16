# -*- coding: utf-8 -*-

#    Copyright 2013-2014 Mirantis, Inc.
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

from kombu import Connection

from nailgun.logger import logger
from nailgin import rpc
from nailgin.rpc import consumer
from nailgun.rpc import receiver


def run():
    logger.info("Starting standalone RPC consumer...")
    with Connection(rpc.conn_str) as conn:
        try:
            consumer.RPCConsumer(conn, receiver.NailgunReceiver).run()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Stopping standalone RPC consumer...")
