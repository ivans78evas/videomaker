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
    - **Security Rule:** You **MUST** open port `6379` (Redis) and `8000` (API) in the Oracle Cloud VCN Security List (Ingress Rules) to allow the Colab worker to connect.
    - **Redis Bind:** The provided `docker-compose.yml` is configured to bind Redis to `0.0.0.0` for external access.
    - **Pro Tip (Upstash):** If you prefer not to manage Redis on your server, use [Upstash](https://upstash.com/). It's free-tier friendly and works over TLS (use `rediss://` scheme in your connection string).
2. **Colab Notebook:**
   - Open the provided `infra/colab_worker/worker_colab.ipynb` in Google Colab.
   - Set the `MASTER_IP` to your OCI server's public IP.
   - Enable **GPU Acceleration** (Edit -> Notebook Settings -> T4 GPU).
   - Run the cells to start the worker.

### Automation
- Use browser extensions like "Auto Refresh Plus" to keep the Colab tab alive.
- For longer tasks, the system supports persistent state, allowing workers to resume from the Redis queue after a restart.

---

## 3. Reliability vs. Cost: Performance Tuning

Choose your configuration based on your Redis provider (Local Docker vs. Upstash).

### Option A: Performance Mode (Local Redis)
*Use this if you are running Redis on your own OCI/Private server.*
- **Action:** In `backend/app/celery_app.py`, you can reduce `broker_transport_options['polling_interval']` to `1` or `2`.
- **Impact:** Near-instant task pickup. High command volume (unlimited on local).

### Option B: Quota-Saver Mode (Upstash / Managed Redis)
*Use this to stay within the 500k monthly command free tier.*
- **Action:** Keep `polling_interval` at `10` or higher.
- **Action:** Ensure `worker_enable_remote_control = False` and `worker_send_task_events = False` to stop unnecessary chatter.
- **Impact:** Slight delay (up to 10s) in task pickup, but saves ~80% of command quota.

### Option C: GPU Persistence (Google Drive)
The Colab worker is pre-configured to mount `/content/drive`.
- **Benefit:** If the Colab runtime disconnects, processed fragments (audio/video clips) are saved to Drive.
- **Resumption:** When you restart the worker, it checks for existing files before re-downloading or re-processing, preventing "burned" credits on synthesis APIs.
