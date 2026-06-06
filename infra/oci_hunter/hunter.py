import oci
import os
import time
import requests
import sys

# --- Configuration (Use Environment Variables) ---
# OCI Config
CONFIG = {
    "user": os.environ.get("OCI_USER_OCID"),
    "key_content": os.environ.get("OCI_KEY_CONTENT"),
    "fingerprint": os.environ.get("OCI_FINGERPRINT"),
    "tenancy": os.environ.get("OCI_TENANCY_OCID"),
    "region": os.environ.get("OCI_REGION"),
}

# Instance details
COMPARTMENT_ID = os.environ.get("OCI_COMPARTMENT_OCID")
SUBNET_ID = os.environ.get("OCI_SUBNET_OCID")
IMAGE_ID = os.environ.get("OCI_IMAGE_OCID") # e.g. Oracle Linux 8 (ARM)
SSH_PUBLIC_KEY = os.environ.get("OCI_SSH_PUBLIC_KEY")
INSTANCE_NAME = os.environ.get("OCI_INSTANCE_NAME", "TranslationTurbo-Master")

# Notifications
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_notification(message):
    print(f"NOTIFICATION: {message}")
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        except Exception as e:
            print(f"Failed to send telegram notification: {e}")

def launch_instance():
    try:
        # Validate config
        for key, val in CONFIG.items():
            if not val:
                print(f"Error: Missing environment variable for {key}")
                return False

        # Initialize OCI client
        # Note: We use key_content instead of a key_file to make it easier for GitHub Actions
        core_client = oci.core.ComputeClient(CONFIG)

        # Build launch details for VM.Standard.A1.Flex (Always Free ARM)
        launch_details = oci.core.models.LaunchInstanceDetails(
            display_name=INSTANCE_NAME,
            compartment_id=COMPARTMENT_ID,
            shape="VM.Standard.A1.Flex",
            shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
                ocpus=4,
                memory_in_gbs=24
            ),
            source_details=oci.core.models.InstanceSourceViaImageDetails(
                image_id=IMAGE_ID
            ),
            create_vnic_details=oci.core.models.CreateVnicDetails(
                subnet_id=SUBNET_ID,
                assign_public_ip=True
            ),
            metadata={
                "ssh_authorized_keys": SSH_PUBLIC_KEY
            },
            is_pv_encryption_in_transit_enabled=True
        )

        print(f"Attempting to launch instance '{INSTANCE_NAME}' in {CONFIG['region']}...")
        response = core_client.launch_instance(launch_details)

        if response.status == 200:
            instance = response.data
            msg = f"✅ SUCCESS! Instance created: {instance.display_name} (OCID: {instance.id})"
            send_notification(msg)
            return True

    except oci.exceptions.ServiceError as e:
        if e.code == "Out-of-capacity" or "Out of host capacity" in e.message:
            print("❌ Capacity empty. Retrying later...")
        elif e.code == "LimitExceeded":
            print("⚠️ Limit Exceeded (maybe you already have an instance?). Stopping.")
            sys.exit(0)
        else:
            print(f"🛑 OCI Service Error: {e.code} - {e.message}")
    except Exception as e:
        print(f"🛑 Unexpected Error: {e}")

    return False

if __name__ == "__main__":
    success = launch_instance()
    if not success:
        sys.exit(1) # Exit with error to allow GitHub Actions to track failure/retry
    else:
        sys.exit(0)
