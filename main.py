import sys
import requests
import pathlib
import json
import validators

workspace = pathlib.Path().resolve() / "workspace"
pathlib.Path(workspace).mkdir(parents=True, exist_ok=True)


def edit_config(operation, node, value):
    with open('config.json', 'r') as json_file:
        data = json.load(json_file)

    if operation == 'add':
        data[node].append(value)

    with open('config.json', 'w') as outfile:
        json.dump(data, outfile)


def download_bins(download_index):
    download_unsuccessful = True
    for index in download_index:
        if index == "1":
            tezos_client_path = workspace / "tezos-client"
            if tezos_client_path.is_file():
                print("tezos-client at path {tezos_client_path} already exists, not downloading".format(tezos_client_path=tezos_client_path))
                download_unsuccessful = False
                continue
            print("downloading tezos-client")
            response = requests.get("https://github.com/serokell/tezos-packaging/releases/latest/download/tezos-client")
            # check response for errors
            with open(tezos_client_path, 'wb') as tez:
                tez.write(response.content)
            edit_config("add", "bin_paths", str(tezos_client_path))
        elif index == "2":
            print("downloaded SmartPy")
        elif index == "3":
            print("downloaded LIGO")
        else:
            print("could not download for index: {index}".format(index=index))
            break
        download_unsuccessful = False
    return download_unsuccessful


if __name__ == "__main__":
    options = [opt for opt in sys.argv[1:] if opt.startswith("--")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    options.append("--init")

    if "--init" in options:

        empty_config = {
            "bin_paths": [],
            "endpoints": [],
            "tests": [],
            "accounts": []
        }
        with open('config.json', 'w') as config:
            config.write(json.dumps(empty_config))

  # ###################### bin
        bin_selection_unsuccessful = True
        while bin_selection_unsuccessful:
            print("Select what to download: 1) tezos-client, 2) SmartPy, 3) LIGO")
            bin_selection = input("e.g. 1,2,3 to download them all: ")
            bin_indexes = []
            selection = bin_selection.split(",")
            if len(selection) == 0:
                print("invalid input")
            else:
                for index in selection:
                    if index == "1":  # tezos
                        bin_indexes.append(index)
                    elif index == "2":  # smartpy
                        bin_indexes.append(index)
                    elif index == "3":  # ligo
                        bin_indexes.append(index)
                    else:
                        print("invalid input: {input}".format(input=index))
                        bin_indexes.clear()
                        break
            if len(bin_indexes) > 0:
                bin_selection_unsuccessful = download_bins(bin_indexes)


# ###################### node
        node_selection_unsuccessful = True
        while node_selection_unsuccessful:
            print("Select what node to connect to: 1) ithacanet.smartpy.io, 2) mainnet.smartpy.io, 3) local or custom input")
            selection = input('e.g. 1,2 or "https://ithacanet.smartpy.io","https://mainnet.smartpy.io" or "https://custom_node.com": ')
            node_selection = selection.split(",")
            if len(node_selection) == 0:
                print("invalid input")
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
                            print("invalid input: {input}".format(input=index))
                            node_url.clear()
                            break

                for url in node_url:
                    edit_config("add", "endpoints", url)

        var = input("hallo: ")
        accounts_selection_unsuccessful = True
        while accounts_selection_unsuccessful:
            pass

    elif "--start" in options:
        print(" ".join(arg.upper() for arg in args))
    elif "--add" in options:
        print(" ".join(arg.lower() for arg in args))
    else:
        raise SystemExit(f"Usage: {sys.argv[0]} ( --init | --start | --add ) <arguments>")
