source ./frontend/deploy/front.sh
source ./backend/deploy/backend.sh


function deploy_front(){
  front_to_remote
}

function deploy_backend() {
    backend_to_remote
}

function deploy() {
    front_to_remote &
    front=$!
    backend_to_remote &
    backend=$!
    wait $front
    wait $backend
}

deploy_front