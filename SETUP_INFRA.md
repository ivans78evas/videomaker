# Infrastructure Setup Guide: Zero-Cost Automation

This guide explains how to set up the automated systems to secure "Always Free" resources for the TranslationTurbo firm.

## 1. Oracle Cloud (OCI) Capacity Hunter
To bypass the "Out of host capacity" error for ARM Ampere (A1) instances, we use a GitHub Actions script that polls the OCI API.

### Prerequisites
1. **OCI Account:** Sign up at [oracle.com/cloud/free/](https://www.oracle.com/cloud/free/).
2. **API Key:**
   - Go to OCI Console -> **User Settings** -> **API Keys**.
   - Click **Add API Key**, download the Private Key (you will need its content).
   - Copy the **Configuration File Snippet** (contains User OCID, Tenancy OCID, Fingerprint, Region).

### GitHub Secrets Setup
In your GitHub repository, go to **Settings** -> **Secrets and variables** -> **Actions** and add the following:

| Secret Name | Value Example |
| :--- | :--- |
| `OCI_USER_OCID` | `ocid1.user.oc1..aaaaaa...` |
| `OCI_TENANCY_OCID` | `ocid1.tenancy.oc1..aaaaaa...` |
| `OCI_FINGERPRINT` | `xx:xx:xx:...` |
| `OCI_KEY_CONTENT` | Paste the content of your `.pem` private key |
| `OCI_REGION` | `eu-frankfurt-1` |
| `OCI_COMPARTMENT_OCID` | Usually same as Tenancy OCID |
| `OCI_SUBNET_OCID` | Go to Networking -> VCN -> Subnets and copy OCID |
| `OCI_IMAGE_OCID` | Find "Oracle Linux 8" (ARM) image OCID for your region |
| `OCI_SSH_PUBLIC_KEY` | Your `ssh-rsa ...` public key for access |
| `TELEGRAM_BOT_TOKEN` | (Optional) Your bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | (Optional) Your Chat ID from @userinfobot |

### Activation
The workflow is located in `.github/workflows/oci_hunter.yml`. It will run every 5 minutes automatically. You can also trigger it manually from the **Actions** tab.

---

## 2. Google Colab "Headless Worker"
Since Google Colab sessions expire, we use a worker script that connects to our Master node's Redis queue.

### Steps
1. **Master Node:** Once your OCI instance is ready, install Docker and run the Master container (Redis/FastAPI).
2. **Colab Notebook:**
   - Open the provided `infra/worker_colab.ipynb` in Google Colab.
   - Set the `MASTER_IP` to your OCI server's public IP.
   - Enable **GPU Acceleration** (Edit -> Notebook Settings -> T4 GPU).
   - Run the cells to start the worker.

### Automation
- Use browser extensions like "Auto Refresh Plus" to keep the Colab tab alive.
- For longer tasks, the system supports persistent state, allowing workers to resume from the Redis queue after a restart.
