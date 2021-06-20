import os
import pickle
import subprocess

from substrateinterface.contracts import ContractCode, ContractInstance
from substrateinterface import SubstrateInterface, Keypair

def get_contract_instance(name, substrate,  keypair, wasm2addr):

    # 1. Build a ContractCode object from the original metadata and wasm files.
    code = ContractCode.create_from_contract_files(
        metadata_file=os.path.join('.', f'{name}.metadata.json'),
        wasm_file=os.path.join('.', f'{name}.wasm'),
        substrate=substrate
    )

    # 2. Given the wasm bytes we can determine if this contract is already deployed by consulting our
    # wasm2addr dict.  This is a hack we use until we find a better way to do this.
    if code.wasm_bytes in wasm2addr:
        contract_addr = wasm2addr[code.wasm_bytes]

        contract_instance = ContractInstance.create_from_address(
            #contract_address="5EX7fMo6TSNqLEj3gKx8ZTkNLRAqQUzCcwBDFsVfRGsUK7yn",
            contract_address=contract_addr,
            metadata_file=os.path.join('.', f'{name}.metadata.json'),
            substrate=substrate
        )

        print(f'The {name} contract is already deployed at address {contract_addr}.')

    else:
        # Deploy contract
        print(f'Deploy {name} contract...')

        try:
            contract_instance = code.deploy(
                keypair=keypair,
                endowment=10 ** 15,
                gas_limit=1000000000000,
                constructor="new",
                args={'init_value': True},
                upload_code=True
            )

        except Exception:
            # This is an error because we should have already known this.
            print(f'The {name} contract is already deployed but we did not already know this.')
            exit()

        contract_addr = contract_instance.contract_address

        wasm2addr[code.wasm_bytes] = contract_addr
        f = open("wasm2addr", "wb")
        f.write(pickle.dumps(wasm2addr))
        f.close()

        print(f'✅ {name} deployed @ {contract_addr}')

    return contract_instance

# This script assumes that docker images substrate-study-flipper and substrate-study-j exist
# and contain the metadata.json and *.wasm files required to load said contract onto the canvas node
# block chain.  This script further assumes that a canvas node block chain is presently executing.

# 1.
# Assuming so, copy the metadata.json and *.wasm from the relevant images to
# the local file system whereupon the script may then use these files to load the flipper and j
# contracts onto the block chain.

# 1.1 flipper

container_id = subprocess.check_output("docker create substrate-study-flipper", shell=True).decode("utf-8").rstrip()
os.system(f"docker cp {container_id}:/root/flipper.wasm ./flipper.wasm")
os.system(f"docker cp {container_id}:/root/metadata.json ./flipper.metadata.json")
os.system(f'docker rm {container_id}')

# 1.2 j

container_id = subprocess.check_output("docker create substrate-study-j", shell=True).decode("utf-8").rstrip()
os.system(f"docker cp {container_id}:/root/j.wasm ./j.wasm")
os.system(f"docker cp {container_id}:/root/metadata.json ./j.metadata.json")
os.system(f'docker rm {container_id}')

# 2. We maintain a dict[wasm bytes] -> contract_address that we serialize/deserialize to and from an external file.
# The purpose of this is to enable us to get the contract address of a previously deployed contract.  We need
# this contract_address for subsequent access to the contract and we cannot presently find a better way to do this.
print(os.getcwd())
try:
    f = open("wasm2addr", "rb")
    wasm2addr = pickle.loads( f.read() )

except:
    wasm2addr = {}

# 3. We'll need a keypair in order to work with the contracts.
keypair = Keypair.create_from_uri('//Alice')

# 4. Connect to the canvas node
try:
    substrate = SubstrateInterface(
        url="ws://127.0.0.1:9944",
        type_registry_preset='canvas'
    )
except:
    print("Cannot connect to the canvas node")
    exit()


# 5. For each contract, obtain a ContractInstance.  Either via a fresh deploy or by finding it via the contract address.
contract_flipper = get_contract_instance('flipper', substrate, keypair, wasm2addr)
contract_j       = get_contract_instance('j', substrate, keypair, wasm2addr)

# 6. Now do some random gyrations to demonstrate that we can work with the contracts

# Check if the contracts are on the chain
contract_info = substrate.query("Contracts", "ContractInfoOf", [contract_flipper.contract_address,])
print(contract_info)

contract_info = substrate.query("Contracts", "ContractInfoOf", [contract_j.contract_address])
print(contract_info)

# Read a current value
result = contract_flipper.read(keypair, 'get')
print('Current value of "get":', result.contract_result_data)

# Do a gas estimation of the message
gas_predit_result = contract_flipper.read(keypair, 'flip')

print('Result of dry-run: ', gas_predit_result.contract_result_data)
print('Gas estimate: ', gas_predit_result.gas_consumed)

# Do the actual transfer
print('Executing contract call...')
contract_receipt = contract_flipper.exec(
keypair, 'flip', args={},
gas_limit=gas_predit_result.gas_consumed
)

print(f'Events triggered in contract: {contract_receipt.contract_events}')

result = contract_flipper.read(keypair, 'get')

print('Current value of "get":', result.contract_result_data)
