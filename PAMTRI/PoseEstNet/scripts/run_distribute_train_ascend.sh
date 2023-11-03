#!/bin/bash
# Copyright 2021 Huawei Technologies Co., Ltd
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
echo "bash run_distribute_train_ascend.sh DATA_PATH pretrain_path RANK_TABLE"
echo "For example: bash run_distribute_train_ascend.sh /path/dataset /path/pretrain_path /path/rank_table"
echo "It is better to use the absolute path."
echo "=============================================================================================================="
set -e
get_real_path(){
  if [ "${1:0:1}" == "/" ]; then
    echo "$1"
  else
    echo "$(realpath -m $PWD/$1)"
  fi
}
DATA_PATH=$(get_real_path $1)
PRETRAINED_PATH=$(get_real_path $2)
RANK_TABLE=$(get_real_path $3)
export DATA_PATH=${DATA_PATH}
export RANK_SIZE=8
export RANK_TABLE_FILE=$RANK_TABLE

EXEC_PATH=$(pwd)
echo "$EXEC_PATH"

export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

cd ../
for((i=1;i<${RANK_SIZE};i++))
do
    rm -rf device$i
    mkdir device$i
    cd ./device$i
    cp ../config.yaml ./
    cp -r ../src ./
    cp ../train.py ./
    export DEVICE_ID=$i
    export RANK_ID=$i
    echo "start training for device $i"
    env > env$i.log
    nohup python3 -u train.py --cfg config.yaml --data_dir ${DATA_PATH} --distribute True --pre_ckpt_path ${PRETRAINED_PATH} > train$i.log 2>&1 &
    echo "$i finish"
    cd ../
done
rm -rf device0
mkdir device0
cd ./device0
cp ../config.yaml ./
cp -r ../src ./
cp ../train.py ./
export DEVICE_ID=0
export RANK_ID=0
echo "start training for device 0"
env > env0.log
nohup python3 -u train.py --cfg config.yaml --data_dir ${DATA_PATH} --distribute True --pre_ckpt_path ${PRETRAINED_PATH} > train0.log 2>&1 &
echo "0 finish"

if [ $? -eq 0 ];then
    echo "training success"
else
    echo "training failed"
    exit 2
fi
echo "finish"
cd ../

