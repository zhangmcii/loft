source ./frontend/deploy/front.sh
source ./backend/deploy/backend.sh

# 捕获Ctrl+C，终止所有子进程
trap 'echo "\n中断，正在终止所有进程..."; jobs -p | xargs -r kill; exit 130' INT


# function deploy_front(){
#   front_to_remote
# }

# function deploy_backend() {
#     backend_to_remote
# }

function deploy() {
    front_to_remote &
    front=$!
    backend_to_remote &
    backend=$!
    wait $front
    wait $backend
}


echo "传入参数: $1"

# 根据参数执行不同的部署函数
if [ "$1" = "frontend" ]; then
  echo "部署前端" 
  front_to_remote
elif [ "$1" = "backend" ]; then
  echo "部署后端" 
  backend_to_remote
else
  echo "部署前后端"
  deploy
fi
