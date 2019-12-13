#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Francois Lallart (@fraff)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
version_added: "2.10"
author: Francois Lallart (@fraff)
short_description: Minimalist wrapper around OVH api and ovh python module
description:
    - Minimalist wrapper around OVH api and ovh python module, see https://api.ovh.com/console for more informations.
requirements: [ "ovh" ]
options:
    path:
        required: true
        type: str
        description:
            - https://api.ovh.com/console/{path} don't forget to replace / with %2f
    method:
        type: str
        choices: ['GET', 'POST', 'PUT', 'DELETE']
        default: 'GET'
        aliases: ['action']
        description:
            - what method to use
    body:
        type: dict
        default:
        aliases: ['data']
        description:
            - use this body if required
    endpoint:
        type: str
        description:
            - The endpoint to use (for instance ovh-eu)
    application_key:
        type: str
        description:
            - The applicationKey to use
    application_secret:
        type: str
        description:
            - The application secret to use
    consumer_key:
        type: str
        description:
            - The consumer key to use
'''

EXAMPLES = '''
# basic
- ovh_api: path="/cloud/project"
- ovh_api:
    path: "/ip/x.x.x.x%2f29/reverse"
    method: "POST"
    body: {'ipReverse': 'y.y.y.y', reverse: 'my.cool.reverse'}

# get info about yourself
- ovh_api: method=GET path=/me
'''

RETURN = '''
'''

import os
import sys
import traceback

try:
    import ovh
    import ovh.exceptions
    from ovh.exceptions import APIError
    HAS_OVH = True
except ImportError:
    HAS_OVH = False
    OVH_IMPORT_ERROR = traceback.format_exc()

from ansible.module_utils.basic import AnsibleModule


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(required=True),
            method=dict(required=False, default='GET', choices=['GET', 'POST', 'PUT', 'DELETE'], aliases=['action']),
            body=dict(required=False, default={}, type='dict', aliases=['data']),
            endpoint=dict(required=False),
            application_key=dict(required=False, no_log=True),
            application_secret=dict(required=False, no_log=True),
            consumer_key=dict(required=False, no_log=True),
        ),
        supports_check_mode=False
    )

    if not HAS_OVH:
        module.fail_json(msg='python-ovh is required to run this module, see https://github.com/ovh/python-ovh')

    # Get parameters
    path = module.params.get('path')
    method = module.params.get('method').lower()
    body = module.params.get('body')
    endpoint = module.params.get('endpoint')
    application_key = module.params.get('application_key')
    application_secret = module.params.get('application_secret')
    consumer_key = module.params.get('consumer_key')

    # Connect to OVH API
    client = ovh.Client(
        endpoint=endpoint,
        application_key=application_key,
        application_secret=application_secret,
        consumer_key=consumer_key
    )

    mydict = {
        'func': {'get': client.get, 'put': client.put, 'post': client.post, 'delete': client.delete},
        'code': {'get': False, 'put': True, 'post': True, 'delete': True}
    }

    try:
        if method in ['put', 'post', 'delete']:
            old = mydict['func']['get'](path, **body)
            result = mydict['func'][method](path, **body)
            new = mydict['func']['get'](path, **body)
            changed = (ordered(old) != ordered(new))
#            module.warn("old: " + str(old['name']))
#            module.warn("new: " + str(new['name']))
#            module.warn(str(changed))
            module.exit_json(changed=changed, result=result)

        else:
            result = mydict['func'][method](path, **body)
            module.exit_json(changed=mydict['code'][method], result=result)

    except APIError as apiError:
        module.fail_json(changed=False, msg="OVH API Error: {0}".format(apiError))

    # We should never reach here
    module.fail_json(msg='Internal ovh_api module error')


if __name__ == "__main__":
    main()
