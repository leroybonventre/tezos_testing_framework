import sys
import requests
import pathlib
import json
import validators

workspace = pathlib.Path().resolve() / "workspace"
pathlib.Path(workspace).mkdir(parents=True, exist_ok=True)


def edit_config(operation, node, key_to_modify, value):
    with open('workspace/config.json', 'r') as json_file:
        data = json.load(json_file)

    if operation == 'add':
        for entry in data:
            if entry == node:
                if not key_to_modify:
                    data[entry].append(value)
                else:
                    for item in data[entry]:
                        my_keys = item.keys()
                        for key in my_keys:
                            if key == key_to_modify:
                                item.update({key: value})

    '''
    
        current_key = node_list[0]

        if current_key in data.keys():
            pass
        data_keys = data.keys()
        for key in data:
            if key == node_list:
                pass
    '''
    '''
    
    for node_list_index, node in enumerate(node_list):
        for entry in data:
            node_list_index += 1
            for item in data[entry]:
                my_key = item.keys()
                if my_key == node_list[node_list_index]:
                    pass
    '''
    '''
    if entry == node_list[node_list_index]:
        pass
    else:
        node_list_index += 1
        break
    if operation == 'add':
        for idx, item in enumerate(data):
            if node_list[idx] in item:
                for idx2, entry in enumerate(data[item]):
                    index_of_key = data[item].index(entry)  # .update({"tezos-client": value})
                    for x in data[item]:
                        x.update({"tezos-client": value})

    '''
    '''
    
    if operation == 'add':
        counter = 0
        for item in node_list:
            counter += 1
            if len(node_list) > counter:
                if item in data.keys():
                    continue
            else:
                print(data[node_list])
                for entry in data[node_list]:
                    test = data[entry].keys()
                    print(test)

               # node_to_add = data[node_list[counter]]
                #print(node_to_add)
    '''

    if operation == 'remove':
        pass

    with open('workspace/config.json', 'w') as outfile:
        json.dump(data, outfile)


def download_bins(indexes_to_download):
    download_unsuccessful = True
    for download_index in indexes_to_download:
        if download_index == "1":
            tezos_client_path = workspace / "tezos-client"
            if tezos_client_path.is_file():
                print("WARNING: tezos-client at path {tezos_client_path} already exists, not downloading".format(tezos_client_path=tezos_client_path))
                download_unsuccessful = False
            else:
                print("INFO: downloading tezos-client")
                response = requests.get("https://github.com/serokell/tezos-packaging/releases/latest/download/tezos-client")
                # ToDo: check response for errors
                with open(tezos_client_path, 'wb') as tez:
                    tez.write(response.content)
            edit_config("add", "bin_paths", "tezos-client", str(tezos_client_path))
        elif download_index == "2":
            print("downloaded SmartPy")
        elif download_index == "3":
            print("downloaded LIGO")
        else:
            print("could not download for index: {index}".format(index=download_index))
            break
        download_unsuccessful = False
    return download_unsuccessful


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

# ###################### bin
        bin_selection_unsuccessful = True
        while bin_selection_unsuccessful:
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


# ###################### node
        node_selection_unsuccessful = True
        while node_selection_unsuccessful:
            print("Select what node to connect to: 1) ithacanet.smartpy.io, 2) mainnet.smartpy.io, 3) local or custom input")
            selection = input('INFO: e.g. 1,2 or "https://ithacanet.smartpy.io","https://mainnet.smartpy.io" or "https://custom_node.com": ')
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
                    for url in node_url:
                        edit_config("add", "endpoints", False, url)

                    node_selection_unsuccessful = False

        # end:  while node_selection_unsuccessful

        accounts_selection_unsuccessful = True
        while accounts_selection_unsuccessful:
            pass

    elif "--start" in options:
        '''
        1. load config
        2. check env
        3. confirm with user
        4. select and start test(s)
        5. save test results
        6. report failed test(s) as output
        '''
        print(" ".join(arg.upper() for arg in args))
    elif "--add" in options:
        print(" ".join(arg.lower() for arg in args))
    else:
        raise SystemExit(f"Usage: {sys.argv[0]} ( --init | --start | --add ) <arguments>")
