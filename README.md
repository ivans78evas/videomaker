# 🚀 TranslationTurbo: The Autonomous Video Translation Firm

TranslationTurbo is a professional-grade, "Zero-Capex" engineering system for mass YouTube video translation. It transforms the foundation of MoneyPrinterTurbo into a distributed, high-fidelity localization factory.

## 🌟 Key Value Propositions

*   **Zero Infrastructure Cost:** Orchestrates "Always Free" tiers from Oracle Cloud (Master), Upstash (Redis), and Google Colab (GPU Workers).
*   **Studio Quality:** Preserves original background music and SFX using Meta's **Demucs**. Strictly avoids quality-degrading time-stretching in favor of intelligent LLM gapping.
*   **Aggregator Intelligence:** Dynamically routes tasks between **Groq, OpenAI, and Gemini** for maximum speed and zero downtime (RecCloud-style).
*   **Human-in-the-Loop (HITL):** Built-in review API and dashboard scaffold for professional-grade quality control (Papercup-style).
*   **Extreme Sustainability:** Redis consumption optimized to **<70k commands/month**, allowing 24/7 operation on free-tier brokers.
*   **Business Ready:** Integrated **50/50 Revenue Share** logic and formal partnership agreement templates.

---

## 🛠 Tech Stack & Architecture

| Layer | Technology |
| :--- | :--- |
| **Backend** | FastAPI, SQLAlchemy 2.0, PostgreSQL |
| **Processing** | Celery, Redis (Managed/Upstash) |
| **Vocal Separation** | Meta Demucs (HDemucs) |
| **Transcription** | Faster-Whisper (Large-v3-Turbo) |
| **Translation** | Groq (Llama 3), Gemini 1.5 Flash, OpenRouter |
| **Synthesis** | Edge-TTS (Narrator), Voice Cloning (Roadmap) |
| **Assembly** | FFmpeg `filter_complex` (Precise multi-segment sync) |
| **Frontend** | Next.js 14, shadcn/ui, TypeScript |

---

## 📈 Dashboard Preview (Scaffold)

The Next.js 14 Operator Dashboard provides a real-time "Pulse" of your autonomous firm:

![Dashboard Overview](https://raw.githubusercontent.com/harry0703/MoneyPrinterTurbo/main/docs/preview.png) *(Placeholder: System UI maps to Next.js components in `/frontend`)*

---

## 📂 Project Structure & The 7-Step Pipeline

The firm operates an automated **7-Step Processing Loop** designed for maximum fidelity:

1.  **Ingestion:** `yt-dlp` fetches high-quality video and playlist metadata.
2.  **Separation:** `HDemucs` isolates vocals from background music and SFX.
3.  **Transcription:** `Faster-Whisper` generates timestamp-accurate transcripts.
4.  **Moderation:** LLM-based safety check filters prohibited content.
5.  **Translation:** `AggregatorService` routes text to Groq/Gemini/OpenAI.
6.  **Synthesis:** `Edge-TTS` generates localized audio segments.
7.  **Assembly:** `FFmpeg` layers audio with millisecond precision (no time-stretching).

### Folder Map
*   [`backend/`](./backend/): The core API and processing services.
*   [`frontend/`](./frontend/): Next.js 14 Operator Dashboard and Partner Portal.
*   [`infra/`](./infra/): Automation scripts for OCI capacity hunting and Headless Colab Workers.
*   [`ANALYSIS_AND_PROPOSAL.md`](./ANALYSIS_AND_PROPOSAL.md): Deep-dive technical analysis and competitor mapping.
*   [`SETUP_INFRA.md`](./SETUP_INFRA.md): Step-by-step guide for "Always Free" deployment.
*   [`PARTNERSHIP_OFFER.md`](./PARTNERSHIP_OFFER.md): Standard 50/50 deal template for content creators.

---

## 🚀 Getting Started

1.  **Infrastructure:** Follow [SETUP_INFRA.md](./SETUP_INFRA.md) to secure your Oracle ARM instance and Upstash Redis.
2.  **Master Node:**
    ```bash
    docker-compose up -d
    ```
3.  **GPU Workers:** Open [`infra/colab_worker/worker_colab.ipynb`](./infra/colab_worker/worker_colab.ipynb) in Google Colab, set your `REDIS_URL`, and hit Run.
4.  **Bulk Ingestion:** Use the API (or Dashboard) to submit a YouTube Playlist URL and watch the firm decompose and process the library.

---

## 🗺 Roadmap (The "Missing Layer")

- [x] **Phase 1-3:** Core Pipeline, Distributed Fleet, and Aggregator Logic.
- [ ] **Phase 4:** [Visual Text Localizer] - PaddleOCR + AI Inpainting for on-screen text replacement.
- [ ] **Phase 5:** [YouTube OAuth2 Publisher] - Fully automated localized uploads.

---

## 📄 License & Legal
This system includes LLM-driven **Content Moderation** to ensure compliance with YouTube's "AI-Altered Content" policies. Partner channels must be whitelisted in the original creator's Content ID.

---
*Created with 🦾 by TranslationTurbo Architects.*
