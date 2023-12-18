import os

import pangea.exceptions as pe
from intel_examples.utils import print_reputation_data
from pangea.config import PangeaConfig
from pangea.services import FileIntel
from pangea.tools import logger_set_pangea_config

token = os.getenv("PANGEA_INTEL_TOKEN")
domain = os.getenv("PANGEA_DOMAIN")
config = PangeaConfig(domain=domain)
intel = FileIntel(token, config=config, logger_name="intel")
logger_set_pangea_config(logger_name=intel.logger.name)


def main():
    print("Checking hash...")

    try:
        indicator = "142b638c6a60b60c7f9928da4fb85a5a8e1422a9ffdc9ee49e17e56ccca9cf6e"
        response = intel.hash_reputation(
            hash=indicator,
            hash_type="sha256",
            provider="reversinglabs",
            verbose=True,
            raw=True,
        )
        print("Result:")
        print_reputation_data(indicator, response.result.data)
    except pe.PangeaAPIException as e:
        print(e)


if __name__ == "__main__":
    main()
