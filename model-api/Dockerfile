FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir torch==2.2.0 --index-url https://download.pytorch.org/whl/cpu --timeout 300

RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn==0.29.0 \
    pytesseract==0.3.13 \
    pdf2image==1.17.0 \
    Pillow==10.4.0 \
    opencv-python-headless==4.9.0.80 \
    numpy==1.26.4 \
    python-multipart==0.0.9 \
    boto3==1.34.0 \
    transformers==4.38.0

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "120"]

