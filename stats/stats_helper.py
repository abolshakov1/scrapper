import json
import pprint


def get_stats_from_file():
    file = './stats.json'
    try:
        with open(file, 'r+') as fp:
            data = json.load(fp)
            # pprint.pprint(data)
            return data
    except Exception as exc:
        print ('Cannot read file', exc)
        return {}


def save_to_file(stats):
    try:
        with open('./stats.json', 'w') as fp:
            json.dump(stats, fp)
    except Exception as exc:
        print('Cannot write to file', exc)
