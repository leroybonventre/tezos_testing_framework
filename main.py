import subprocess
import sys
import requests
import pathlib
import json
import validators
import stat

workspace = pathlib.Path().resolve() / "workspace"
pathlib.Path(workspace).mkdir(parents=True, exist_ok=True)


def insert_options(list_of_cmd, list_to_insert, starting_position=0, replace=False):
    for value in list_to_insert:
        if replace:
            list_of_cmd[starting_position] = value
        else:
            list_of_cmd.insert(starting_position, value)
    return list_of_cmd


def run_line(config_data, string_of_cmd, string_expected_output, save_output_location):
    """ running a test from the config. returns True if the test passed without errors and interception """
    # ToDo: read cli params form the current test's config

    list_of_cmd = string_of_cmd.split(' ', -1)
    if list_of_cmd[0] not in {'tezos-client', 'SmartPy', 'LIGO'}: # change this to list from config "bin_paths"
        print('invalid command! Command can not start with: {first_cmd}'.format(first_cmd=list_of_cmd[0]))
    else:
        if list_of_cmd[0] == 'tezos-client':
            # ToDo: wtf is this mess, who did this?
            my_list = [str(get_config_value(config_data, 'tezos-client'))]
            list_of_cmd = insert_options(list_of_cmd, my_list, 0, True)
            list_of_cmd = insert_options(list_of_cmd, ['-E'], 1, False)
            list_of_cmd = insert_options(list_of_cmd, ['{endpoint}'.format(endpoint=get_config_value(config_data, 'endpoints')[0])], 2, False)
            print("list_of_cmd: ")
            print(list_of_cmd)
            result = subprocess.run(list_of_cmd, capture_output=True, text=True)
            if result.returncode > 0:
                # ToDo: better output of the ran command with parameter
                print("got errors running: '{string_of_cmd}'".format(string_of_cmd=string_of_cmd))
                print(result)
                print(result.stderr)
                return False
            else:
                return True


def get_config():
    """ reads the config and returns it """
    try:
        with open('workspace/config.json', 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError as e:
        print("ERROR: could not open file 'workspace/config.json', stopping!")
        print(e)
        sys.exit()


def get_config_value(search_data, search_key):
    my_return = ''
    for top_level in search_data:
        if type(top_level) == type(search_key):
            if top_level == search_key:
                return search_data[top_level]
            else:
                my_return = get_config_value(search_data[top_level], search_key)
                if my_return != '':
                    return my_return
        # ToDo: check for list to shorten this
        else:
            if type(top_level) == dict:
                for key in top_level.keys():
                    if key == search_key:
                        return top_level.get(key)
                    else:
                        return ""
            my_return = get_config_value(data[top_level], search_key)
            if my_return != '':
                return my_return
    return my_return


def edit_config(operation, node, key_to_modify, value):
    config_data = get_config()

    if operation == 'add':
        for config_entry in config_data:
            if config_entry == node:
                if not key_to_modify:
                    config_data[config_entry].append(value)
                else:
                    for item in config_data[config_entry]:
                        my_keys = item.keys()
                        for key in my_keys:
                            if key == key_to_modify:
                                item.update({key: value})

    # ToDo: account for more operations in order to edit tests and test-accounts
    if operation == 'remove':
        pass

    with open('workspace/config.json', 'w') as outfile:
        json.dump(config_data, outfile)


def download_bins(indexes_to_download):
    download_unsuccessful = True
    for download_index in indexes_to_download:
        if download_index == "1":
            tezos_client_path = workspace / "tezos-client"
            if tezos_client_path.is_file():
                print("WARNING: tezos-client at path {tezos_client_path} already exists, not downloading".format(
                    tezos_client_path=tezos_client_path))
            else:
                print("INFO: downloading tezos-client")
                response = requests.get(
                    'https://github.com/serokell/tezos-packaging/releases/latest/download/tezos-client')
                # ToDo: check response for errors
                with open(tezos_client_path, 'wb') as tez:
                    tez.write(response.content)
                # make bin executable
                tezos_client_path.chmod(tezos_client_path.stat().st_mode | stat.S_IEXEC)

            edit_config("add", "bin_paths", "tezos-client", str(tezos_client_path))
            download_unsuccessful = False
        elif download_index == "2":
            print("downloaded SmartPy")
        elif download_index == "3":
            print("downloaded LIGO")
        else:
            print("could not download for index: {index}".format(index=download_index))
            break
    return download_unsuccessful


# ToDo: add verbose output
if __name__ == "__main__":
    options = [opt for opt in sys.argv[1:] if opt.startswith("--")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    # debug:
    options.append("--init")

    if "--init" in options:

        # check if config exists, else use this new one
        config_path = workspace / "config.json"
        if config_path.is_file():
            pass
        else:
            empty_config = {
                "bin_paths": [{"tezos-client": ""}, {"SmartPy": ""}, {"LIGO": ""}],
                "endpoints": [],
                "tests": [],
                "accounts": []
            }
            with open('workspace/config.json', 'w') as config:
                config.write(json.dumps(empty_config))

        config_data = get_config()

        # 3 things need to be done: select bin path, select a node, setup an account

        bin_selection_unsuccessful = True
        while bin_selection_unsuccessful:
            print()
            print("Select what to download: 1) tezos-client, 2) SmartPy, 3) LIGO")
            bin_selection = input("INFO: e.g. 1,2,3 to download them all: ")
            bin_indexes = []
            selection = bin_selection.split(",")
            if len(selection) == 0:
                print("INFO: invalid input")
            else:
                for index in selection:
                    if index == "1":  # tezos
                        bin_indexes.append(index)
                    elif index == "2":  # SmartPy
                        bin_indexes.append(index)
                    elif index == "3":  # LIGO
                        bin_indexes.append(index)
                    else:
                        print("WARNING: invalid input: {input}".format(input=index))
                        bin_indexes.clear()
                        break
            if len(bin_indexes) > 0:
                bin_selection_unsuccessful = download_bins(bin_indexes)

        # end:  while bin_selection_unsuccessful

        node_selection_unsuccessful = True
        while node_selection_unsuccessful:
            print()
            print(
                "Select what node to connect to: 1) ithacanet.smartpy.io, 2) mainnet.smartpy.io, 3) local or custom input")
            selection = input(
                'INFO: e.g. 1,2 or "https://ithacanet.smartpy.io","https://mainnet.smartpy.io" or "https://custom_node.com": ')
            node_selection = selection.split(",")
            if len(node_selection) == 0:
                print("WARNING: invalid input")
            else:
                node_url = []
                for index in node_selection:
                    if index == "1":
                        node_url.append("https://ithacanet.smartpy.io")
                    elif index == "2":
                        node_url.append("https://mainnet.smartpy.io")
                    elif index == "3":
                        node_url.append("http://127.0.0.1:9732")
                    else:
                        if validators.url(index):
                            node_url.append(index)
                        else:
                            print("WARNING: invalid input: {input}".format(input=index))
                            node_url.clear()
                            break

                if len(node_url):
                    current_endpoints = get_config_value(config_data, 'endpoints')
                    for url in node_url:
                        if url in current_endpoints:
                            continue
                        edit_config("add", "endpoints", False, url)
                    node_selection_unsuccessful = False
        # end:  while node_selection_unsuccessful

        # ToDo: maybe later save the content of the account json into the config
        accounts_selection_unsuccessful = True
        while accounts_selection_unsuccessful:
            print()
            print('Testnet accounts can be created at: https://teztnets.xyz')
            print('absolut path to the account json file')
            path_to_check = input("INFO: e.g. account1.json or /home/leroy/Documents/account1.json: ")
            path_to_check = pathlib.Path(path_to_check)
            account_name = ''
            if path_to_check.is_file():
                current_account = {}
                with open(path_to_check, 'r') as file:
                    new_account = json.load(file)
                account_name = path_to_check.stem
                add_account = False
                if len(config_data['accounts']) == 0:
                    add_account = True
                else:
                    for counter, account in enumerate(config_data['accounts']):
                        if list(account.keys())[counter] == account_name:
                            print("WARNING: account with the name '{account}' already exists, not adding a new one!".format(account=account_name))
                            continue
                        else:
                            add_account = True

                if add_account:
                    current_account[account_name] = new_account
                    edit_config("add", "accounts", False, current_account)

            else:
                print("ERROR: '{path_to_check}' does not exist, try again!".format(path_to_check=path_to_check))
                continue

            account_activation_results = []
            for account in config_data['accounts']:
                account_values = json.dumps(account.get(account_name))
                account_values = account_values.replace(" ", "")
                line_to_run = "tezos-client activate account {account_name} with {account_values}".format(account_name=account_name, account_values=account_values)
                result = run_line(config_data, line_to_run, '', '')
                account_activation_results.append(result)

            if False in account_activation_results:
                pass
            else:
                accounts_selection_unsuccessful = False
        # end:  while accounts_selection_unsuccessful

        '''
        config_init_unsuccessful = True
        while config_init_unsuccessful:
            line_to_run = '{}'.format()
            result = run_line(config_data, line_to_run, '', '')

        '''
        # end:  while config_init_unsuccessful
        # ToDo: "config init" and test the config

    # end: --init

    elif "--start" in options:
        start_unsuccessful = True
        while start_unsuccessful:

            # ToDo: check env, accounts,
            config_path = workspace / "config.json"
            if config_path.is_file():
                with open('workspace/config.json', 'r') as json_file:
                    data = json.load(json_file)
                start_unsuccessful = False
            else:
                print("no config")

            for entry in data["bin_paths"]:
                for path in entry.values():
                    if path == '':
                        pass
                    else:
                        path_to_check = pathlib.Path(path)
                        if path_to_check.is_file():
                            start_unsuccessful = False
                        else:
                            print("file {entry} does not exist!".format(entry=entry))

            # check node availability

            json_data = get_config()
            tezos_bin_path = get_config_value(json_data, "tezos-client")
            endpoints = get_config_value(json_data, "endpoints")
            for url in endpoints:
                pass
                # $TEZOSCLIENT transfer 1 from deploy to KT1PWx2mnDueood7fEmfbBDKx1D9BAnnXitn
                run_line(json_data, "tezos-client transfer 1 from account1 to account2", "", False)
                '''
                response = requests.get(url)
                if response.status_code != 200:
                    start_unsuccessful = True
                    print("endpoint: {current_endpoint} not reachable! aborting".format(current_endpoint=url))
                    break
                # use tezos to check url with requests
                '''

        '''
        1. load config
        2. check env
        3. confirm with user
        4. select and start test(s)
        5. save test results
        6. report failed test(s) as output
        '''
        print(" ".join(arg.upper() for arg in args))

    # end: --start

    # ToDo:
    elif "--add" in options:
        print(" ".join(arg.lower() for arg in args))

    # end: --add

    else:
        raise SystemExit(f"Usage: {sys.argv[0]} ( --init | --start | --add ) <arguments>")
