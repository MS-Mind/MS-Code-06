#!/bin/bash
# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

echo "=============================================================================================================="
echo "Please run the script as: "
echo "bash run_eval_gpu.sh DATASET_NAME ONNX_PATH DEVICE_ID HEATMAP_SEGMENT"
echo "For example: bash run_eval_gpu.sh ../data/ ./*.onnx 0 h"
echo "It is better to use the absolute path."
echo "=============================================================================================================="

if [ $# != 4 ]; then
  echo "bash run_eval_gpu.sh DATASET_NAME ONNX_PATH DEVICE_ID HEATMAP_SEGMENT"
  exit 1
fi

set -e
get_real_path(){
  if [ "${1:0:1}" == "/" ]; then
    echo "$1"
  else
    echo "$(realpath -m $PWD/$1)"
  fi
}
DATA_PATH=$(get_real_path $1)
ONNX_PATH=$(get_real_path $2)
PROJECT_DIR=$(cd "$(dirname "$0")" || exit; pwd)
if [ "$4" == "h" ] || [ "$4" == "s" ];then
    if [ "$4" == "h" ];then
      need_heatmap=True
      need_segment=False
    else
      need_heatmap=False
      need_segment=True
    fi
else
    echo "heatmap_segment must be h or s"
    exit 1
fi

EXEC_PATH=$(pwd)
echo "$EXEC_PATH"

export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

export RANK_SIZE=1

python ${PROJECT_DIR}/../eval_onnx.py --root ${DATA_PATH} \
  --onnx_path ${ONNX_PATH} \
  --device_id $3 \
  --device_target GPU \
  --heatmapaware ${need_heatmap} \
  --segmentaware ${need_segment} > ${PROJECT_DIR}/../eval_onnx_gpu.log 2>&1 &
