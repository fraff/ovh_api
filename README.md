# [ovh_api](https://github.com/fraff/ovh_api)
Minimalist ansible python module wrapper around OVH api and ovh python module

## Requirements

- python-ovh: https://github.com/ovh/python-ovh

## exemples

      - name: get dedicated servers list
        ovh_api:
          path: "/dedicated/server"
          method: "GET"
        register: result3

      - name: get dedicated servers details
        ovh_api:
          path: "/dedicated/server/{{ item }}"
          method: "GET"
        with_items: "{{ result3.result }}"
        register: result4
        loop_control:
          label: "{{ item }} / {{ result4.result.reverse }}"

      - name: reboot one of them randomly
        ovh_api:
          path: "/dedicated/server/{{ result3.result | random }}/reboot"
          method: "POST"

