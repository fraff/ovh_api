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

DOCUMENTATION = '''
---
module: ovh_api
author: Francois (fraff) Lallart
short_description: Minimalist wrapper around OVH api and ovh python module
description:
    - Enable 
requirements: [ "ovh" ]
options:
    path
        required: true
        description:
            - https://api.ovh.com/console/{path}
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
# basic
- ovh_api: path="/cloud/project"
- ovh_api:
    path: "/ip/x.x.x.x%2f29/reverse"
    method: "POST"
    body: {'ipReverse': 'y.y.y.y', reverse: 'my.cool.reverse'}
'''

import os
import sys

try:
    import ovh
    import ovh.exceptions
    from ovh.exceptions import APIError
except ImportError:
    print "failed=True msg='ovh required for this module'"
    sys.exit(1)


def main():
    module = AnsibleModule(
        argument_spec = dict(
            path = dict(required=True),
            method = dict(required=False, default='GET', choices=['GET', 'POST', 'PUT', 'DELETE'], aliases=['action']),
            body = dict(required=False, default={}, type=dict, aliases=['data'])
        ),
        supports_check_mode = False
    )

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


# import module snippets
from ansible.module_utils.basic import *

main()
