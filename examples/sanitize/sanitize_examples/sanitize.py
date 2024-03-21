import datetime
import os

import pangea.exceptions as pe
from pangea.config import PangeaConfig
from pangea.response import TransferMethod
from pangea.services import Sanitize

# Get service credentials
token = os.getenv("PANGEA_SANITIZE_TOKEN")
assert token
domain = os.getenv("PANGEA_DOMAIN")
assert domain

# Create service object
config = PangeaConfig(domain=domain)
sanitize = Sanitize(token, config=config)

# Provide path to a test file for sanitization
filepath = "./sanitize_examples/testfile.pdf"

# Create a unique file name
date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
name = f"{date}_{os.path.basename(filepath)}"

def main():
    try:
        print("Sanitizing a file...")

        # Open file for read in binary mode
        with open(filepath, "rb") as f:
            # Create a unique file name

            # Request file sanitization using the `sanitize` method:
            # The SDK will upload the file for sanitization and respond with the results. 
            # Upon successful completion, a presigned GET URL for downloading the sanitized file
            # will be provided in `result.dest_url` within the response.
            #
            # Note that internally, the SDK will use a presigned POST URL for uploading the file,
            # for which both `file` and `upload_file_name` parameters are required.
            response = sanitize.sanitize(
                transfer_method=TransferMethod.POST_URL,
                file=f, 
                uploaded_file_name=name
            )

            print(f"\n\nUse this URL to download the sanitized file: \n{response.result.dest_url}")
    except pe.PangeaAPIException as e:
        print(f"Sanitize request error: {e.response.summary}")
        for err in e.errors:
            print(f"\t{err.detail} \n")

if __name__ == "__main__":
    main()
