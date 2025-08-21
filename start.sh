#!/bin/bash

# 启动后端服务
echo "启动后端服务..."
cd backend
python flasky.py &
BACKEND_PID=$!

# 启动前端服务
echo "启动前端服务..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# 捕获CTRL+C信号，关闭所有进程
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

# 等待所有进程完成
wait

# echo "服务已启动:"
# echo "- 后端API: http://localhost:5000"
# echo "- 前端应用: http://localhost:8080"
