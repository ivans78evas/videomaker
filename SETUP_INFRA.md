# Инфраструктура и масштабирование: От 0 до Бесконечности

Система TranslationTurbo спроектирована так, чтобы стоимость инфраструктуры росла линейно только вместе с вашей прибылью.

---

## Этап 1: Zero-Capex (Старт без вложений)
**Цель:** Получить первые кейсы и первые деньги.
- **Master Node:** Oracle Cloud Always Free (ARM Ampere A1).
- **GPU Workers:** Google Colab (Tesla T4).
- **Broker:** Upstash Redis (Free Tier).
- **Затраты:** $0 / мес.
- **Мощность:** ~2-3 видео в час.

## Этап 2: Производственная эффективность (Vast.ai / Clore.ai)
**Цель:** Масштабирование на 10+ каналов.
- **Master Node:** Переезд на VPS за $5-10/мес (DigitalOcean / Hetzner).
- **GPU Workers:** Аренда инстансов на Vast.ai (RTX 3060 12GB).
- **Затраты:** ~$30-50 / мес на GPU (при 24/7 загрузке одного воркера).
- **Мощность:** ~20-30 видео в час.

## Этап 3: Корпоративный уровень (RunPod / Lambda)
**Цель:** Работа с миллионными каналами и VIP-заказы.
- **GPU Workers:** RunPod Secure Cloud (A100 / H100) для сверхбыстрого рендеринга и тяжелых LLM.
- **Затраты:** $200+ / мес.
- **Мощность:** Сотни видео в сутки.

---

## Инструкция по запуску воркера на Vast.ai

1.  **Выбор инстанса:**
    - Зайдите на [vast.ai](https://vast.ai/console/create/).
    - В фильтрах выберите: `GPU RAM >= 12GB`, `DLPerf >= 10`.
    - Сортировка по `Price (Inc. Storage)`.
2.  **Настройка Docker:**
    - Используйте образ `python:3.11-slim` или наш кастомный.
    - В `On-start script` вставьте:
      ```bash
      apt-get update && apt-get install -y ffmpeg git
      pip install celery redis torch torchaudio yt-dlp
      git clone https://github.com/your-repo/translation-turbo.git
      cd translation-turbo/backend
      celery -A app.celery_app worker --loglevel=info -Q default,bulk_tasks
      ```
3.  **Переменные окружения:**
    - Не забудьте прописать `CELERY_BROKER_URL` и `OPENROUTER_API_KEY`.

---

## Почему P2P-маркетплейсы выгоднее облаков?
- **Цена:** В 10-20 раз дешевле AWS/Google Cloud.
- **Конфиденциальность:** Вы полностью контролируете инстанс.
- **Гибкость:** Можно арендовать 10 штук RTX 3060 на 1 час для "залпового" перевода целого плейлиста, а затем выключить их.
