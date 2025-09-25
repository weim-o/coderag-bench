#!/bin/bash

# 切换到指定目录
cd /home/coderag_bench/aad-fastapi-dlg/aad_fastapi_dlg-0.0.3

# 激活 conda 环境
source /root/miniconda3/etc/profile.d/conda.sh
conda activate aad_fastapi_dlg

# 判断是否有用户命令
if [ $# -eq 0 ]; then
    # 没有参数 → 启动交互 bash
    exec /bin/bash
else
    # 有参数 → 执行用户命令
    exec "$@"
fi