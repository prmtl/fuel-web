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
from nailgun.extensions.volume_manager import manager
from nailgun.test import base
from nailgun import utils

import mock


class TestDefaultDiskHandler(base.BaseIntegrationTest):

    def test_pre_70_node_with_cluster(self):
        self.env.create(
            release_kwargs={
                'version': '2016.1-6.1'
            },
            nodes_kwargs=[{
                'roles': ['controller', ],
                'meta': {
                    'disks': [
                        {
                            u'disk': u'disk/by-path/pci-000:00:09.0-some-disk',
                            u'size': 1000204886016,
                            u'name': u'sda',
                            u'model': u'TOSHIBA MK1002TS'
                        },
                    ]
                }
            }]
        )
        node = self.env.nodes[0]
        resp = self.app.get(utils.reverse(
            'NodeDefaultsDisksHandler',
            kwargs={'node_id': node.id}))
        disk_info = resp.json

        volumes_info = disk_info[0].pop('volumes')
        self.assertEqual(
            disk_info,
            [{
                u'extra': [],
                u'id': u'disk/by-path/pci-000:00:09.0-some-disk',
                u'name': u'sda',
                u'size': 953241,
            }]
        )
        self.assertItemsEqual(
            volumes_info,
            [
                {u'keep_data': False, u'name': u'os', u'size': 55296},
                {u'keep_data': False, u'name': u'image', u'size': 897945}
            ]
        )

    def test_70_node_with_cluster(self):
        self.env.create(
            release_kwargs={
                'version': '2016.1-7.0'
            },
            nodes_kwargs=[{
                'roles': ['controller', ],
                'meta': {
                    'disks': [
                        {
                            u'disk': u'disk/by-path/pci-000:00:09.0-some-disk',
                            u'size': 1000204886016,
                            u'name': u'sda',
                            u'model': u'TOSHIBA MK1002TS',
                        },
                    ]
                }
            }]
        )
        node = self.env.nodes[0]
        resp = self.app.get(utils.reverse(
            'NodeDefaultsDisksHandler',
            kwargs={'node_id': node.id}))
        disk_info = resp.json

        volumes_info = disk_info[0].pop('volumes')
        self.assertEqual(
            disk_info,
            [{
                u'extra': [],
                u'id': u'disk/by-path/pci-000:00:09.0-some-disk',
                u'name': u'sda',
                u'size': 953241,
            }]
        )
        self.assertItemsEqual(
            volumes_info,
            [
                {u'keep_data': False, u'name': u'os', u'size': 55296},
                {u'keep_data': False, u'name': u'image', u'size': 897945}
            ]
        )

    @mock.patch('nailgun.extensions.volume_manager.handlers.'
                'disks.get_volume_manager')
    def test_pre_70_node_no_cluster(self, mock_get_vm):
        mock_get_vm.side_effect = lambda node: manager.VolumeManager(node)

        node = self.env.create_node(
            roles=['controller', ],
            meta={
                'disks': [{
                    u'disk': u'disk/by-path/pci-000:00:09.0-some-disk',
                    u'size': 1000204886016,
                    u'name': u'sda',
                    u'model': u'TOSHIBA MK1002TS',
                }]
            }
        )
        resp = self.app.get(utils.reverse(
            'NodeDefaultsDisksHandler',
            kwargs={'node_id': node['id'], 'old_format': True}))

        self.assertEqual(
            resp.json,
            [{
                u'id': u'disk/by-path/pci-000:00:09.0-some-disk',
                u'name': u'sda',
                u'size': 953369,
                u'volumes': [],
                u'extra': [],
            }]
        )

    def test_70_node_no_cluster(self):
        node = self.env.create_node(
            roles=['controller', ],
            meta={
                'disks': [{
                    u'disk': u'disk/by-path/pci-000:00:09.0-some-disk',
                    u'size': 1000204886016,
                    u'name': u'sda',
                    u'model': u'TOSHIBA MK1002TS',
                }]
            }
        )
        resp = self.app.get(utils.reverse(
            'NodeDefaultsDisksHandler',
            kwargs={'node_id': node['id']}))

        self.assertEqual(
            resp.json,
            {
                'parteds': [
                    {
                        'id': 1,
                        'label': '',
                        'device': 'disk/by-path/pci-000:00:09.0-some-disk',
                        'name': 'sda',
                        'partitions': [],
                    }
                ]
            }
        )


class TestDiskHandler(base.BaseIntegrationTest):

    def test_put_pre_70(self):
        # cluster = self.env.create(
        #     release_kwargs={
        #         'version': '2016.1-6.1'
        #     },
        #     node_kwargs=[{
        #         'roles': ['controller', ]
        #     }]
        # )
        # node = cluster.nodes[0]
        # reps = self.app.get(
        #     utils.reverse(
        #         'NodeDisksHandler',
        #         kwargs={'node_id': node.id}),
        #     params=jsonutils.dumps({}),
        # )g
        # import pdb; pdb.set_trace()
        pass

    def test_put_70(self):
        pass


class TestNodeDiscovery(base.BaseIntegrationTest):
    pass
