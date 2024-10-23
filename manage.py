from flask_script import Manager
from flask import url_for
from app import create_app

manager = Manager(create_app)


@manager.command
def routes():
    output = []
    for rule in manager.app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = "{:50s} {:20s} {}".format(rule.endpoint, methods, url)
        output.append(line)

    for line in sorted(output):
        print(line)


if __name__ == '__main__':
    manager.run()
