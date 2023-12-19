import os

import pangea.exceptions as pe
from intel_examples.ip.utils import print_ip_geolocate_bulk_data
from pangea.config import PangeaConfig
from pangea.services import IpIntel

token = os.getenv("PANGEA_INTEL_TOKEN")
domain = os.getenv("PANGEA_DOMAIN")
config = PangeaConfig(domain=domain)
intel = IpIntel(token, config=config)


def main():
    print("Geolocate IP...")

    try:
        response = intel.geolocate_bulk(ips=["93.231.182.110", "24.235.114.61"], verbose=True, raw=True)
        print("Result:")
        print_ip_geolocate_bulk_data(response.result.data)
    except pe.PangeaAPIException as e:
        print(e)


if __name__ == "__main__":
    main()