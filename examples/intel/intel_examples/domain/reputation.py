import os

import pangea.exceptions as pe
from intel_examples.utils import print_reputation_data
from pangea.config import PangeaConfig
from pangea.services import DomainIntel

token = os.getenv("PANGEA_INTEL_TOKEN")
domain = os.getenv("PANGEA_DOMAIN")
config = PangeaConfig(domain=domain)
intel = DomainIntel(token, config=config)


def main():
    print("Checking domain...")

    try:
        indicator = "737updatesboeing.com"
        response = intel.reputation(domain=indicator, provider="domaintools", verbose=True, raw=True)
        print("Result:")
        print_reputation_data(indicator, response.result.data)
    except pe.PangeaAPIException as e:
        print(e)


if __name__ == "__main__":
    main()
