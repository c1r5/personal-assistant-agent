#!/bin/bash

# Deploy script para subir containers e verificar status
# Baseado no workflow de produção

set -e  # Para o script se algum comando falhar

echo "🚀 Iniciando deploy dos containers..."

# Parar containers existentes
echo "📦 Parando containers existentes..."
docker compose down

# Subir containers com build
echo "🔨 Construindo e subindo containers..."
docker compose up --build -d

# Esperar 2 segundos para os containers inicializarem
echo "⏳ Aguardando 2 segundos para inicialização..."
sleep 2

# Verificar status dos containers
echo "🔍 Verificando status dos containers..."
docker compose ps

# Verificar se todos os containers estão rodando
RUNNING_CONTAINERS=$(docker compose ps --services --filter "status=running" | wc -l)
TOTAL_CONTAINERS=$(docker compose ps --services | wc -l)

echo ""
echo "📊 Status do deploy:"
echo "   Containers rodando: $RUNNING_CONTAINERS"
echo "   Total de containers: $TOTAL_CONTAINERS"

if [ "$RUNNING_CONTAINERS" -eq "$TOTAL_CONTAINERS" ]; then
    echo "✅ Deploy realizado com sucesso! Todos os containers estão rodando."
    exit 0
else
    echo "❌ Erro no deploy! Nem todos os containers estão rodando."
    echo "🔍 Verificando logs dos containers com problema..."
    docker compose logs --tail=20
    exit 1
fi
