FROM python:3.9-slim

# Install system dependencies for LibreOffice and PDF tools
# fonts-liberation: Arial/Times/Courier replacements
# fonts-crosextra-carlito: Calibri replacement
# fonts-crosextra-caladea: Cambria replacement
RUN apt-get update && apt-get install -y \
    libreoffice-writer \
    libreoffice-java-common \
    default-jre \
    fonts-liberation \
    fonts-dejavu \
    fonts-crosextra-carlito \
    fonts-crosextra-caladea \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    && rm -rf /var/lib/apt/lists/*

# Configure Font Aliasing
COPY fonts.conf /etc/fonts/local.conf

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create uploads directory
RUN mkdir -p uploads

EXPOSE 7860

CMD ["flask", "run", "--host=0.0.0.0", "--port=7860"]
