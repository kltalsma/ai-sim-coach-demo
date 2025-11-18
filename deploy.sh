#!/bin/bash

# AI Sim Racing Coach - Deployment Script for Sirus (62.131.114.32)

set -e

SERVER="kltalsma@62.131.114.32"
REMOTE_PATH="~/ai-sim-coach-demo"
LOCAL_PATH="$HOME/Prive/AI/ai-sim-coach-demo"

echo "=================================================="
echo "AI Sim Racing Coach - Deployment to Sirus"
echo "=================================================="
echo ""

# Step 1: Copy files to server
echo "[1/4] Copying files to server..."
rsync -avz --progress \
    --exclude '.git' \
    --exclude '*.pyc' \
    --exclude '__pycache__' \
    --exclude '.env' \
    "$LOCAL_PATH/" "$SERVER:$REMOTE_PATH/"

echo ""
echo "[2/4] Copying .env file (edit if needed)..."
scp "$LOCAL_PATH/.env" "$SERVER:$REMOTE_PATH/.env"

echo ""
echo "[3/4] Connecting to server and starting Docker containers..."
ssh "$SERVER" << 'ENDSSH'
    cd ~/ai-sim-coach-demo
    
    echo "Stopping existing containers..."
    docker-compose down || true
    
    echo "Building and starting new containers..."
    docker-compose up -d --build
    
    echo "Waiting for services to start..."
    sleep 10
    
    echo "Container status:"
    docker-compose ps
    
    echo ""
    echo "Backend logs (last 20 lines):"
    docker logs --tail 20 ai-sim-coach-backend
ENDSSH

echo ""
echo "[4/4] Deployment complete!"
echo ""
echo "=================================================="
echo "Access URLs:"
echo "=================================================="
echo "Custom Dashboard: http://62.131.114.32:8124/ai-sim-coach/"
echo "Grafana:          http://62.131.114.32:3000/ai-sim-coach/grafana/"
echo "API:              http://62.131.114.32:5001"
echo "API Status:       http://62.131.114.32:5001/api/status"
echo ""
echo "WebSocket:        ws://62.131.114.32:5001/ws"
echo ""
echo "=================================================="
echo "Useful Commands:"
echo "=================================================="
echo "View logs:        ssh $SERVER 'cd $REMOTE_PATH && docker-compose logs -f'"
echo "Stop services:    ssh $SERVER 'cd $REMOTE_PATH && docker-compose down'"
echo "Restart services: ssh $SERVER 'cd $REMOTE_PATH && docker-compose restart'"
echo "=================================================="
