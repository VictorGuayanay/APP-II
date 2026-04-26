# Usar imagen oficial de Python Bullseye
FROM python:3.11-slim-bullseye

# Configuración básica
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Paso 1: Instalar herramientas base y COMPILADORES
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    unixodbc-dev \
    gcc \
    g++ \
    build-essential

# Paso 2: Instalar la llave de Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/microsoft.gpg

# Paso 3: Añadir el repositorio de Microsoft
RUN echo "deb [arch=amd64] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# Paso 4: Actualizar e instalar el driver
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools

# Paso 5: Configurar el PATH para los tools de SQL
ENV PATH="$PATH:/opt/mssql-tools/bin"

# Paso 6: Limpiar
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Configuración de la APP (Ajustada para trabajar desde la raíz del repo)
WORKDIR /app

# Copiamos el requirements desde la carpeta backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el contenido de la carpeta backend al directorio de trabajo
COPY backend/ .

# Exponer puerto (Fly.io usa 8080 por defecto)
EXPOSE 8080

# Comando de inicio usando el puerto que asigne Fly.io
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-8080} --workers 2"]
