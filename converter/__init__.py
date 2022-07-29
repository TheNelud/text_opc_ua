import xml.etree.ElementTree as ET
import os
import os.path
from opcua import ua


def get_ua_type(value):
    if value.__class__.__name__ == 'int':
        return ua.uatypes.VariantType.Int32
    elif value.__class__.__name__ == 'float':
        return ua.uatypes.VariantType.Float
    elif value.__class__.__name__ == 'bool':
        return ua.uatypes.VariantType.Boolean
    elif value.__class__.__name__ == 'str':
        return ua.uatypes.VariantType.String
    elif value.__class__.__name__ == 'double':
        return ua.uatypes.VariantType.Float
    else:
        return None


def get_config(configFile='cfg.xml'):
    tree = ET.parse(configFile)
    root = tree.getroot()
    res = {}
    for child in root:
        res[child.tag] = child.text

    return res


def last_file(directory):
    files = [os.path.join(directory, _) for _ in os.listdir(directory) if _.endswith('.txt')]
    if len(files) > 0:
        return max(files, key=os.path.getctime)
    else:
        return False


def get_file(dir):
    res = []
    fl = last_file(dir)
    if fl != False:
        for line in open(fl, 'r'):
            line = line.strip()
            res.append(dict(zip(("tag", "date", "value", "Status"), line.split(","))))
        for i in range(len(res)):
            if 'Status' in res[i]:
                res[i]['Status'] = 'Bad'
            else:
                res[i]['Status'] = 'Good'
        return res
    else:
        return False
