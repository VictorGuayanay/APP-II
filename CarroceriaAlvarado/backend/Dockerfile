# Usar imagen oficial de Python Bullseye
FROM python:3.11-slim-bullseye

# Configuración básica
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Paso 1: Instalar herramientas base
RUN apt-get update && apt-get install -y curl gnupg2 unixodbc-dev

# Paso 2: Instalar la llave de Microsoft directamente en el llavero de confianza de APT
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/microsoft.gpg

# Paso 3: Añadir el repositorio de Microsoft (sin el signed-by, ya que está en el llavero global)
RUN echo "deb [arch=amd64] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# Paso 4: Actualizar e instalar el driver
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools

# Paso 5: Configurar el PATH
ENV PATH="$PATH:/opt/mssql-tools/bin"

# Paso 6: Limpiar
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Configuración de la APP
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Exponer puerto y comando de inicio
EXPOSE 5001
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-5001} --workers 2"]
