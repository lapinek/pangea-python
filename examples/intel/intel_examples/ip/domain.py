import os

import pangea.exceptions as pe
from intel_examples.ip.utils import print_ip_domain_data
from pangea.config import PangeaConfig
from pangea.services import IpIntel

token = os.getenv("PANGEA_INTEL_TOKEN")
domain = os.getenv("PANGEA_DOMAIN")
config = PangeaConfig(domain=domain)
intel = IpIntel(token, config=config)


def main():
    print("Get IP's Domain...")

    try:
        ip = "24.235.114.61"
        response = intel.get_domain(ip=ip, provider="digitalelement", verbose=True, raw=True)
        print_ip_domain_data(ip, response.result.data)
    except pe.PangeaAPIException as e:
        print(e)


if __name__ == "__main__":
    main()
