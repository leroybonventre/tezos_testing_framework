# tezos_testing_framework



# Testing Framework

## what
testing framework for running and defining tests to run angainst different protocol versions of tezos.
Protable with a minimal Python environment and an extensiv config file.
Reporting with json.
Accessible with an automated setup.


## setup
'''bash
git clone URL
cd tezos_testing_framework
python3 -m venv
sudo apt install python3-pip
pip install requests pathlib validators
source venv/bin/activate
'''


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
			"tezos-client": "/path/to/tezos-client"
		},
		{
			"SmartPy": "/path/to/SmartPy"
		},
		{
			"LIGO": "/path/to/LIGO"
		}
	],
	"endpoints": ["https://ithacanet.smartpy.io"],
	"tests": [{
		"1": {
			"metadata": {
				"name": "test1",
				"create_date": "2022-01-01"
			},
			"bins": ["tezos-client"],
			"test_string": ["tezos-client transfer 1 from account1 to account2"],
			"accounts": ["account1", "account2"],
			"endpoints": ["https://ithacanet.smartpy.io"]
		}
	}],
	"accounts": [{
		"account1": {
			"pkh": "tz1QwBdkjVdKeik5kv22TTsWHZKLYWGTsvcL",
			"mnemonic": [
				"night",
				"jelly",
				"among",
				"voyage",
				"lesson",
				"video",
				"chunk",
				"clerk",
				"illegal",
				"occur",
				"lift",
				"goose",
				"cover",
				"scatter",
				"inside"
			],
			"email": "wodoykkh.gwpkcgps@teztnets.xyz",
			"password": "16J4kONKxi",
			"amount": "77019740071",
			"activation_code": "bd74e118df73e55b085f041e1f61a6aef1b54e10"
		}
	}, {
		"account2": {
			"pkh": "tz1MqUBgWxfpJgknGMiiJhupei3ZqdSynX39",
			"mnemonic": [
				"fan",
				"uniform",
				"borrow",
				"student",
				"method",
				"sword",
				"spray",
				"two",
				"acquire",
				"cable",
				"text",
				"chest",
				"exile",
				"depart",
				"where"
			],
			"email": "oqlecgnm.uwczdnpf@teztnets.xyz",
			"password": "HvA2bf1bUZ",
			"amount": "121999420072",
			"activation_code": "ed0771d6b163cb1e819bd1520462e7f458be933a"
		}
	}]
}


### empty config
{
    "bin_paths": [],
    "endpoints": [],
    "tests": [],
    "accounts": []
}
