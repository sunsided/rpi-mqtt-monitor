import ast
import os
import subprocess
import config


def get_assignments(filename):
    with open(filename) as f:
        tree = ast.parse(f.read(), filename)

    assignments = {node.targets[0].id: ast.literal_eval(node.value) for node in ast.walk(tree) if isinstance(node, ast.Assign)}
    return assignments


def update_config(current_config, example_config):
    current_assignments = get_assignments(current_config)
    example_assignments = get_assignments(example_config)

    missing_assignments = {var: value for var, value in example_assignments.items() if var not in current_assignments}

    if missing_assignments:
        with open(current_config, 'a') as f:
            for var, value in missing_assignments.items():
                f.write('\n{} = {!r}'.format(var, value))


def display_config_differences(current_config, example_config, display=True):
    current_assignments = get_assignments(current_config)
    example_assignments = get_assignments(example_config)

    missing_assignments = {var: value for var, value in example_assignments.items() if var not in current_assignments}

    if missing_assignments:
        if display: 
            print("Missing variables:")
            for var, value in missing_assignments.items():
                print('\n{} = {!r}'.format(var, value))
        return True
    else:
        return False

def update_config_version(version, script_dir):
    with open(script_dir + '/config.py', 'r') as f:
        lines = f.readlines()

    with open(script_dir + '/config.py', 'w') as f:
        print(":: Updating config version to {}".format(version))
        for line in lines:
            if 'version = ' in line:
                f.write('version = "{}"\n'.format(version))
            else:
                f.write(line)


def do_update(version=config.version, git_update=True, config_update=True):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    print("Current version: {}".format(config.version))
    if git_update:
        print(":: Updating git repository")
        result = subprocess.run(['git', '-C', script_dir, 'pull'], check=True, universal_newlines=True, stdout=subprocess.PIPE)
        print(result.stdout)

    if display_config_differences(script_dir + '/config.py', script_dir + '/config.py.example') and config_update:
        print(":: Updating config.py")
        update_config(script_dir + '/config.py',script_dir + '/config.py.example')

    if version != config.version:
        update_config_version(version, script_dir)


if __name__ == '__main__':   
    do_update()