#!/bin/bash

set -e

echo "Iniciando proceso de build..."

echo "Instalando dependencias..."
pip install -r requirements/production.txt

echo "Recolectando archivos estaticos..."
python manage.py collectstatic --noinput

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Build completado exitosamente!"
