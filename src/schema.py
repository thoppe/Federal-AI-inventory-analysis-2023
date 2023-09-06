import yaml
import json


class Schema:
    def __init__(self, f_yaml):
        # Load in a multistream YAML file, there must be a "key" entry
        stream = open(f_yaml, "r")
        self.data = {}
        for item in yaml.load_all(stream, yaml.FullLoader):
            if "key" not in item:
                print(item)
                raise KeyError("Missing 'key' for YAML entry")

            self.data[item["key"]] = item

    def __repr__(self):
        return json.dumps(self.data, indent=2)

    def get(self, key, **kwargs):
        return self[key].format(**kwargs)

    def __getitem__(self, key, **kwargs):
        return self.data[key]["prompt"].replace(r"\n", "\n")
