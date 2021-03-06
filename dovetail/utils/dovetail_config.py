#!/usr/bin/env python
#
# grakiss.wanglei@huawei.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
#

import yaml
import os


class DovetailConfig(object):

    dovetail_config = {}

    @classmethod
    def load_config_files(cls, conf_path):
        with open(os.path.join(conf_path, 'dovetail_config.yml')) as f:
            cls.dovetail_config = yaml.safe_load(f)

        for extra_config_file in cls.dovetail_config['include_config']:

            # The yardstick and bottlenecks config files are with Jinja2.
            # They need to be parsed later.
            # All other config files should be transfer to like this gradually.
            if extra_config_file.startswith(("yardstick", "bottlenecks")):
                continue
            else:
                file_path = os.path.join(conf_path, extra_config_file)
                with open(file_path) as f:
                    extra_config = yaml.safe_load(f)
                    cls.dovetail_config.update(extra_config)

        path = os.path.join(conf_path, cls.dovetail_config['cli_file_name'])
        with open(path) as f:
            cmd_yml = yaml.safe_load(f)
            cls.dovetail_config['cli'] = cmd_yml[cmd_yml.keys()[0]]

    # update dovetail_config dict with the giving path.
    # if path is in the dovetail_config dict, its value will be replaced.
    # if path is not in the dict, it will be added as a new item of the dict.
    @classmethod
    def update_config(cls, config_dict):
        for key, value in config_dict.items():
            path_list = []
            for item in value['path']:
                path_list.append([(k.strip()) for k in item.split('/')])
            for path in path_list:
                cls.update_non_envs(path, value['value'])

    @staticmethod
    def set_leaf_dict(dic, path, value):
        for key in path[:-1]:
            dic = dic.setdefault(key, {})
        dic[path[-1]] = value

    @classmethod
    def update_non_envs(cls, path, value):
        if value:
            cls.set_leaf_dict(cls.dovetail_config, path, value)
