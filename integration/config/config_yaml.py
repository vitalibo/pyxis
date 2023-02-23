from typing import Dict

import yaml

from pyboost import function
from pyboost.config import ConfigParser


class YamlConfigParser(ConfigParser):
    """
    A configuration parser that uses YAML.
    """

    test = function(lambda x: x.endswith('.yaml') or x.endswith('.yml'))

    def parse(self, content: str) -> Dict:
        return yaml.safe_load(content)
