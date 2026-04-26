# Usar imagen oficial de Python Bullseye
FROM python:3.11-slim-bullseye

# Configuración básica
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Paso 1: Instalar herramientas base
RUN apt-get update && apt-get install -y curl gnupg2 unixodbc-dev

# Paso 2: Configurar la llave de seguridad de Microsoft de forma moderna
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

# Paso 3: Añadir el repositorio de Microsoft específicamente para Bullseye y AMD64
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# Paso 4: Actualizar e instalar el driver (msodbcsql17)
# Incluimos mssql-tools por si acaso se necesitan dependencias compartidas
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools

# Paso 5: Configurar el PATH para los tools de SQL (opcional pero útil)
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
