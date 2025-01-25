FROM python:3.9-slim
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    libx11-dev \
    libxkbfile-dev \
    libgdk-pixbuf2.0-0 \
    libxext6 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig \
    libxrender1 \
    libasound2 \
    libatk1.0-0 \
    libgtk-3-0 \
    chromium-driver \
    chromium
WORKDIR /scrapper
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]