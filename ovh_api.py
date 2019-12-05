#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ovh_api, an Ansible module for accessing ovh api
# Copyright (C) 2019, Francois Lallart <fraff@free.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = '''
---
module: ovh_api
author: Francois Lallart (@fraff)
short_description: Minimalist wrapper around OVH api and ovh python module
description:
    - Minimalist wrapper around OVH api and ovh python module
requirements: [ "ovh" ]
options:
    path
        required: true
        description:
            - https://api.ovh.com/console/{path} don't forget to replace / with %2f
    method:
        required: true
        choices: ['GET', 'POST', 'PUT', 'DELETE']
        aliases: ['action']
        description:
            - obvious
    body:
        required: false
        default: 
        description:
            - use this body if required
'''

EXAMPLES = '''
# list your cloud projects
- ovh_api: path="/cloud/project"

# set a reverse to your x.x.x.x/29 ip block
- ovh_api:
    path: "/ip/x.x.x.x%2f29/reverse"
    method: "POST"
    body: {'ipReverse': 'y.y.y.y', reverse: 'my.cool.reverse'}

# get info about yourself
- ovh_api: method=GET path=/me
'''

import os
import sys

try:
    import ovh
    import ovh.exceptions
    from ovh.exceptions import APIError
    HAS_OVH = True
except ImportError:
    HAS_OVH = False

from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(
        argument_spec = dict(
            path = dict(required=True),
            method = dict(required=False, default='GET', choices=['GET', 'POST', 'PUT', 'DELETE'], aliases=['action']),
            body = dict(required=False, default={}, type='dict', aliases=['data'])
        ),
        supports_check_mode = False
    )

    if not HAS_OVH:
        module.fail_json(msg='ovh-api python module is required to run this module ')

    # Get parameters
    path = module.params.get('path')
    method = module.params.get('method').lower()
    body = module.params.get('body')

    # Connect to OVH API
    client = ovh.Client()

    mydict = {
        'func': {'get': client.get, 'put': client.put, 'post': client.post, 'delete': client.delete},
        'code': {'get': False, 'put': True, 'post': True, 'delete': True}
    }

    try:
        result = mydict['func'][method](path, **body)
        module.exit_json(changed=mydict['code'][method], result=result)

    except APIError as apiError:
        module.fail_json(changed=False, msg="OVH API Error: {0}".format(apiError))

    # We should never reach here
    module.fail_json(msg='Internal ovh_api module error')

if __name__ == "__main__":
    main()
