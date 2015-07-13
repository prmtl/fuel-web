# -*- coding: utf-8 -*-

#    Copyright 2013 Mirantis, Inc.
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

"""
Handlers dealing with disks
"""
from distutils.version import StrictVersion

from .. import manager
from nailgun.api.v1.handlers.base import BaseHandler
from nailgun.api.v1.handlers.base import content
from nailgun.api.v1.validators.node import NodeDisksValidator
from nailgun import objects


def get_volume_manager(node):
    if node.cluster and StrictVersion(
            node.cluster.release.environment_version) < StrictVersion('7.0'):
        return manager.VolumeManager(node)
    return manager.VolumeManagerV2(node)


class NodeDisksHandler(BaseHandler):
    """Node disks handler."""

    validator = NodeDisksValidator

    @content
    def GET(self, node_id):
        """:returns: JSONized node disks.

        :http: * 200 (OK)
               * 404 (node not found in db)
        """
        from ..extension import VolumeManagerExtension

        node = self.get_object_or_404(objects.Node, node_id)
        node_volumes = VolumeManagerExtension.get_volumes(node)
        return manager.DisksFormatConvertor.format_disks_to_simple(
            node_volumes)

    @content
    def PUT(self, node_id):
        """:returns: JSONized node disks.

        :http: * 200 (OK)
               * 400 (invalid disks data specified)
               * 404 (node not found in db)
        """
        node = self.get_object_or_404(objects.Node, node_id)
        vm = get_volume_manager(node)

        volumes_data = self.checked_data(
            self.validator.validate,
            node=node,
            # vm=vm,
        )

        if node.cluster:
            objects.Cluster.add_pending_changes(
                node.cluster,
                'disks',
                node_id=node.id
            )

        vm.set_volumes(volumes_data)
        return vm.get_volumes()


class NodeDefaultsDisksHandler(BaseHandler):
    """Node default disks handler."""

    @content
    def GET(self, node_id):
        """:returns: JSONized node disks.

        :http: * 200 (OK)
               * 404 (node or its attributes not found in db)
        """
        node = self.get_object_or_404(objects.Node, node_id)
        if not node.attributes:
            raise self.http(404)

        vm = get_volume_manager(node)
        return vm.get_default_volumes_conf()


class NodeVolumesInformationHandler(BaseHandler):
    """Node volumes information handler."""

    @content
    def GET(self, node_id):
        """:returns: JSONized volumes info for node.

        :http: * 200 (OK)
               * 404 (node not found in db)
        """
        node = self.get_object_or_404(objects.Node, node_id)
        if node.cluster is None:
            raise self.http(404, 'Cannot calculate volumes info. '
                                 'Please, add node to an environment.')
        volumes_info = manager.DisksFormatConvertor.get_volumes_info(node)
        return volumes_info
