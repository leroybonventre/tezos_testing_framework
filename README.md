# tezos_testing_framework



# Testing Framework

## what
testing framework for running and defining tests to run angainst different protocol versions of tezos.
Protable with a minimal Python environment and an extensiv config file.
Reporting with json.
Accessible with an automated setup.


## setup

	git clone URL
	cd tezos_testing_framework
	python3 -m venv
	sudo apt install python3-pip
	pip install requests pathlib validators stat
	source venv/bin/activate



## how
cli to interact with the script and config editing with text editors
workflow should be: start script with one of sevral options

$ python3 my_script.py --init

 (python env???)
 (test accounts???)

    1. confirm what to download. (SmartPy, LIGO, tezos-client)
    2. confirm installation path
    3. select a node. the config will be saved in $HOME/.tezos-client/config (tezos-client -E https://ithacanet.smartpy.io config init)
    4. ask for path to account.json
    5. activate account(s) for testing (tezos-client activate account account1 with /path/to/account.json)
    6. test setup
    n. save config
    
    

    
$ python3 my_script.py --start "1,2"

    1. load config
    2. check env
    3. confirm with user
    4. start test(s)
    5. save test results
    6. report failed test(s) as output
    
$ python3 my_script.py --add "tezos-client transfer 1 from account1 to account2"

    1. user input: test name, select accaunts, select/add endpoints, select bins
    . save to config

### example config
    {
        "bin_paths": [{
            "tezos-client": "/home/leroy/PycharmProjects/tezos_testing_framework/workspace/tezos-client"
        }, {
            "SmartPy": ""
        }, {
            "LIGO": ""
        }],
        "endpoints": ["https://ithacanet.smartpy.io"],
        "tests": [
            {
				"metadata": {
					"name": "test1",
					"create_date": "2022-01-01"
				},
				"bins": ["tezos-client"],
				"test_string": ["tezos-client transfer 1 from account1 to account2"],
				"accounts": ["account1", "account2"],
				"endpoints": ["https://ithacanet.smartpy.io"]
			}
		],
        "accounts": [{
            "account1": {
                "pkh": "tz1eCoue9XZMaAFtH4vAojGAGQWZ4sdN477E",
                "mnemonic": ["whisper", "pulp", "skill", "elder", "foam", "social", "result", "wreck", "benefit", "sorry", "bicycle", "grunt", "exhaust", "oyster", "zebra"],
                "email": "alhqrklc.gkhlwkom@teztnets.xyz",
                "password": "7Cy6X2Juh1",
                "amount": "11854920453",
                "activation_code": "82c2b205e7a517eec8c0f2fd1fa4dd73ffa050b7"
            }
        }]
    }

	