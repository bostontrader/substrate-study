import os
import subprocess

from substrateinterface.contracts import ContractCode, ContractInstance
from substrateinterface import SubstrateInterface, Keypair

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

# 2. Connect to the canvas node
# try:
substrate = SubstrateInterface(
    url="ws://127.0.0.1:9944",
    type_registry_preset='canvas'
)

# 3. We'll need a keypair in order to work with the contracts.
keypair = Keypair.create_from_uri('//Alice')

# 4. Now deploy the contracts if they're not already deployed.

# 4.1 flipper
# Upload WASM code
code = ContractCode.create_from_contract_files(
    metadata_file=os.path.join('.', 'flipper.metadata.json'),
    wasm_file=os.path.join('.', 'flipper.wasm'),
    substrate=substrate
)

# Deploy contract
print('Deploy flipper contract...')

try:
    contract = code.deploy(
        keypair=keypair,
        endowment=10 ** 15,
        gas_limit=1000000000000,
        constructor="new",
        args={'init_value': True},
        upload_code=True
    )

    print(f'✅ Flipper deployed @ {contract.contract_address}')

except Exception:
    print("The flipper contract is already deployed.")


# 4.2 j
# Upload WASM code
code = ContractCode.create_from_contract_files(
    metadata_file=os.path.join('.', 'j.metadata.json'),
    wasm_file=os.path.join('.', 'j.wasm'),
    substrate=substrate
)

# Deploy contract
print('Deploy j contract...')

try:
    contract = code.deploy(
        keypair=keypair,
        endowment=10 ** 15,
        gas_limit=1000000000000,
        constructor="new",
        args={'init_value': True},
        upload_code=True
    )

    print(f'✅ j Deployed @ {contract.contract_address}')

except Exception:
    print("The j contract is already deployed.")
