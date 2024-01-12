import os
import time

import pangea.exceptions as pe
from pangea.config import PangeaConfig
from pangea.services import Vault
from pangea.services.vault.models.asymmetric import AsymmetricAlgorithm
from pangea.services.vault.models.common import KeyPurpose
from pangea.utils import str2str_b64


def main():
    token = os.getenv("PANGEA_VAULT_TOKEN")
    domain = os.getenv("PANGEA_DOMAIN")
    config = PangeaConfig(domain=domain)
    vault = Vault(token, config=config)

    try:
        # Set a unique name.
        name = f"Python sign example {int(time.time())}"

        # Create an asymmetric key with the default parameters.
        create_response = vault.asymmetric_generate(
            algorithm=AsymmetricAlgorithm.Ed25519, purpose=KeyPurpose.SIGNING, name=name
        )
        key_id = create_response.result.id

        # Sign a message.
        text = "hello world"
        msg = str2str_b64(text)
        print(f"text to sign: {text}")
        sign_response = vault.sign(key_id, msg)
        signature = sign_response.result.signature
        print(f"Signature: {signature}")

        # Verify the message's signature.
        print("Verifying...")
        verify_response = vault.verify(key_id, msg, signature)
        if verify_response.result.valid_signature:
            print("Signature verified successfully")
        else:
            print("Invalid signature")

    except pe.PangeaAPIException as e:
        print(f"Vault Request Error: {e.response.summary}")
        for err in e.errors:
            print(f"\t{err.detail} \n")


if __name__ == "__main__":
    main()
