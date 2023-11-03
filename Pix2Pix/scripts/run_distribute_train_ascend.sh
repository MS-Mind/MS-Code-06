#!/bin/bash
# Copyright 2021-2022 Huawei Technologies Co., Ltd
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

if [ $# != 2 ]
then
    echo "Usage: bash scripts/run_distribute_train_gpu.sh [DATASET_PATH] [DATASET_NAME]"
    exit 1
fi

echo "After running the script, the network runs in the background. The log will be generated in LOGx/log.txt"

get_real_path(){
  if [ "${1:0:1}" == "/" ]; then
    echo "$1"
  else
    echo "$(realpath -m $PWD/$1)"
  fi
}

export RANK_SIZE=8
export DEVICE_NUM=8
export RANK_TABLE_FILE=$(get_real_path $1)
export DATASET_PATH=$(get_real_path $2)

for((i=0;i<$DEVICE_NUM;i++))
do
        export DEVICE_ID=$i
        rm -rf ./train_parallel$i
        mkdir ./train_parallel$i
        mkdir ./train_parallel$i/results
        mkdir ./train_parallel$i/results/fake_img
        mkdir ./train_parallel$i/results/ckpt
        mkdir ./train_parallel$i/results/predict
        mkdir ./train_parallel$i/results/loss_show
        cp -r ../src ./train_parallel$i
        cp -r ../*.py ./train_parallel$i
        cp -r ../*.yaml ./train_parallel$i
        cd ./train_parallel$i || exit
        export RANK_ID=$i
        export DEVICE_ID=$i
        echo "start training for rank $i, device $DEVICE_ID"
        env > env.log

        python train.py --run_distribute=1 --device_target=Ascend \
                        --device_id=$DEVICE_ID --train_data_dir=$DATASET_PATH &> log &
        cd ..
done
