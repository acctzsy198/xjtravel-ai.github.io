#!/bin/bash
echo "启动 ngrok 隧道..."
ngrok http 8080 --log=stdout > ngrok.log 2>&1 &
echo "等待隧道建立..."
sleep 5
echo "ngrok 日志输出："
cat ngrok.log
