#!/bin/bash

function front_to_remote(){
    base_path=""
    win_path="/e/project/vue-proj/responsive_new"
    m_path="/Users/nizhenshi/Documents/proj/loft/frontend"

    intel_path="/Users/v/Documents/proj_1/loft_1/frontend"

    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # MSYS或Cygwin环境通常在Windows上运行
        echo "操作系统: Windows"
        base_path=$win_path
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # Darwin内核通常是macOS系统
        echo "操作系统: macOS"
        # 检测Mac的芯片类型
        if sysctl -n machdep.cpu.brand_string | grep -q "Apple"; then
            echo "芯片类型: Apple M系列 (ARM架构)"
            base_path=$m_path
        else
            echo "芯片类型: Intel (x86_64架构)"
            base_path=$intel_path
        fi
    else
        # 其他操作系统
        echo "操作系统: 未知 (${OSTYPE})"
    fi
    echo base_path: $base_path
    
    # 对项目打包
    cd $base_path
    npm run build --mode=production

    # 本地打包目录
    LOCAL_BUILD_DIR="dist"
    # 服务器目录
    SERVER_DIR="/usr/share/nginx/html"

    # 压缩本地dist目录
    echo "压缩本地dist目录..."
    tar -czf dist.tar.gz -C $LOCAL_BUILD_DIR .

    ssh $ROMOTE_USER@$ROMOTE_HOST "echo '删除远程目录旧文件...'; rm -rf $SERVER_DIR/*;"

    echo '传输文件开始...';
    scp dist.tar.gz $ROMOTE_USER@$ROMOTE_HOST:$SERVER_DIR
    if [[ $? -eq 0 ]];then
        echo "传输成功 $LOCAL_FILE"
    else
        echo "传输失败"
    fi

    ssh $ROMOTE_USER@$ROMOTE_HOST "cd $SERVER_DIR; echo '解压压缩文件'; tar -xzf dist.tar.gz -C . --no-xattrs;echo '删除远程压缩包'; rm dist.tar.gz"

    # 删除本地压缩包
    echo "删除本地压缩包..."
    rm -f dist.tar.gz   
    echo "前端部署完成！"
}