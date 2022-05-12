import subprocess
import sys
import requests
import pathlib
import json
import validators
import stat


workspace = pathlib.Path().resolve() / "workspace"
pathlib.Path(workspace).mkdir(parents=True, exist_ok=True)
config_path = workspace / "config.json"


def print_and_get_input(lines_to_print):
    for line in lines_to_print:
        print(line)
    return input('> ')


def choose_from_config(values_for_key):
    for option_counter, value in enumerate(values_for_key):
        print('{option_counter}) {value}'.format(option_counter=option_counter+1, value=value))

    option_selection = print_and_get_input(['', 'select one of the options. e.g. 1'])
    return values_for_key[int(option_selection)-1]


def insert_options(list_of_cmd, list_to_insert, starting_position=0, replace=False):
    for value in list_to_insert:
        if replace:
            list_of_cmd[starting_position] = value
        else:
            list_of_cmd.insert(starting_position, value)
    return list_of_cmd


def run_line(config_data, string_of_cmd, string_expected_output, save_output_location):
    """ running a test from the config. returns True if the test passed without errors and interception """

    list_of_cmd = string_of_cmd.split(' ')
    # ToDo: change this to list of keys from config "bin_paths"
    if list_of_cmd[0] not in {'tezos-client', 'SmartPy', 'LIGO'}:
        print('ERROR: invalid command! Command can not start with: {first_cmd}'.format(first_cmd=list_of_cmd[0]))
        return False

    if list_of_cmd[0] == 'tezos-client':
        my_list = [str(get_config_value(config_data, 'tezos-client'))]
        list_of_cmd = insert_options(list_of_cmd, my_list, 0, True)

    run_result = subprocess.run(list_of_cmd, capture_output=True, text=True)
    if run_result.returncode > 0:
        # ToDo: better output of the ran command with parameter
        print("got errors running: '{string_of_cmd}'".format(string_of_cmd=string_of_cmd))
        return False
    else:
        return True


def get_config():
    """ reads the config and returns it """
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError as e:
        print("ERROR: could not open file '{config_path}', stopping!".format(config_path=config_path))
        print(e)
        sys.exit()


def get_config_value(search_data, search_key):
    """ returns all values for a given key """
    
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
            my_return = get_config_value(search_data[top_level], search_key)
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

    with open(config_path, 'w') as outfile:
        json.dump(config_data, outfile)


def download_bins(download):

    if download == 'tezos-client':
        tezos_client_path = workspace / 'tezos-client'
        if tezos_client_path.is_file():
            print("INFO: tezos-client at path '{tezos_client_path}' already exists, not downloading".format(
                tezos_client_path=tezos_client_path))
        else:
            print('INFO: downloading tezos-client')
            response = requests.get(
                'https://github.com/serokell/tezos-packaging/releases/latest/download/tezos-client')
            if response.status_code != 200:
                print('ERROR: downloading tezos-client failed, aborting!')
                sys.exit()
            with open(tezos_client_path, 'wb') as tez:
                tez.write(response.content)
            tezos_client_path.chmod(tezos_client_path.stat().st_mode | stat.S_IEXEC)  # make bin executable

        edit_config("add", "bin_paths", "tezos-client", str(tezos_client_path))


# ToDo: add verbose output
'''
print_log(level, msg, to_file)
'''

if __name__ == "__main__":
    options = [opt for opt in sys.argv[1:] if opt.startswith("--")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    # debug:
    options.append("--init")

    if "--init" in options:

        # check if config exists, else use this new one

        if config_path.is_file():
            pass
        else:
            empty_config = {
                "bin_paths": [{"tezos-client": ""}, {"SmartPy": ""}, {"LIGO": ""}],
                "endpoints": [],
                "tests": [],
                "accounts": []
            }
            with open(config_path, 'w') as config:
                config.write(json.dumps(empty_config))

        config_data = get_config()

        # 3 things need to be done: select bin path, select a node, setup an account

        bin_selection_unsuccessful = True
        bins = {
            1: 'tezos-client',
            2: 'SmartPy'
        }
        while bin_selection_unsuccessful:
            keep_going = True
            bin_selection = print_and_get_input(['', 'Select what to download: 1) tezos-client, 2) SmartPy, 3) LIGO', 'INFO: e.g. 1,2,3 to download them all'])
            bin_selection = bin_selection.split(",")

            if len(bin_selection) == 0:
                continue

            for counter, entry in enumerate(bin_selection):
                try:
                    bin_selection[counter] = int(bin_selection[counter])  # ToDo: why do I get a type warning?
                except ValueError:
                    keep_going = False
                    break

            if keep_going:
                for item in bin_selection:
                    if item not in bins.keys():
                        keep_going = False
                        break

            if keep_going:
                for download_index in bin_selection:
                    download_bins(bins.get(download_index))
                    bin_selection_unsuccessful = False

            if not keep_going:
                print('WARNING: invalid input, retry')

        # end:  while bin_selection_unsuccessful

        node_selection_unsuccessful = True
        while node_selection_unsuccessful:
            node_selection = print_and_get_input(['', 'Select what node to connect to: 1) ithacanet.smartpy.io, 2) mainnet.smartpy.io, 3) local or custom input', 'INFO: e.g. 1,2 or "https://ithacanet.smartpy.io","https://mainnet.smartpy.io" or "https://custom_node.com"'])
            node_selection = node_selection.split(",")
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

        accounts_selection_unsuccessful = True
        while accounts_selection_unsuccessful:
            path_to_check = print_and_get_input(['', 'testnet accounts can be created at: https://teztnets.xyz', 'absolut path to the account json file', 'INFO: e.g. account1.json or /home/leroy/Documents/account1.json'])
            path_to_check = pathlib.Path(path_to_check)
            account_name = ''
            if path_to_check.is_file():
                pass
            else:
                print("ERROR: '{path_to_check}' does not exist, try again!".format(path_to_check=path_to_check))
                continue

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
                        accounts_selection_unsuccessful = False
                        continue
                    else:
                        add_account = True

                if add_account:
                    current_account[account_name] = new_account
                    edit_config("add", "accounts", False, current_account)
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

        config_init_unsuccessful = True
        while config_init_unsuccessful:
            all_values_for_key = get_config_value(config_data, 'endpoints')
            selected_endpoint = choose_from_config(all_values_for_key)
            line_to_run = 'tezos-client -E {endpoint} config init'.format(endpoint=selected_endpoint)
            result = run_line(config_data, line_to_run, '', '')
            if result:
                config_init_unsuccessful = False

        # end:  while config_init_unsuccessful
        # ToDo: "config init" and test the config

    # end: --init

    elif "--start" in options:
        start_unsuccessful = True
        while start_unsuccessful:

            # ToDo: check env, accounts,
            config_data = get_config()

            found_bins = []
            for entry in config_data["bin_paths"]:
                for path in entry.values():
                    if path == '':
                        pass
                    else:
                        path_to_check = pathlib.Path(path)
                        if path_to_check.is_file():
                            found_bins.append(True)
                        else:
                            print("file '{entry}' does not exist!".format(entry=entry))
                            found_bins.append(False)

            if False in found_bins:
                pass
            else:
                start_unsuccessful = True
                continue

            if len(config_data['accounts']) >= 1:
                pass
            else:
                start_unsuccessful = True
                print('ERROR: no accounts found in config, stopping')
                continue

            if len(config_data['endpoints']) >= 1:
                pass
            else:
                start_unsuccessful = True
                print('ERROR: no endpoints found in config, stopping')
                continue

            # check node availability
            '''
            json_data = get_config()
            tezos_bin_path = get_config_value(json_data, "tezos-client")
            endpoints = get_config_value(json_data, "endpoints")
            for url in endpoints:
                pass
                # $TEZOSCLIENT transfer 1 from deploy to KT1PWx2mnDueood7fEmfbBDKx1D9BAnnXitn
                run_line(json_data, "tezos-client transfer 1 from account1 to account2", "", False)
                
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
