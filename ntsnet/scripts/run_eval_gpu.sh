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

if [ $# -lt 3 ] ||  [ $# -gt 4 ]
then 
    echo "Usage: bash run_eval_gpu.sh [DATA_URL] [TRAIN_URL] [CKPT_FILENAME] [DEVICE_ID(optional)]"
exit 1
fi

export DEVICE_ID=0

if [ $# = 4 ] ; then
  export DEVICE_ID=$4
fi;


get_real_path(){
  if [ "${1:0:1}" == "/" ]; then
    echo "$1"
  else
    echo "$(realpath -m $PWD/$1)"
  fi
}

PATH1=$(get_real_path $1)
PATH2=$(get_real_path $2)
PATH3=$3

if [ ! -d $PATH1 ]
then 
    echo "error: DATA_URL=$PATH1 is not a directory"
exit 1
fi 

if [ ! -d $PATH2 ]
then 
    echo "error: TRAIN_URL=$PATH2 is not a directory"
exit 1
fi

ulimit -u unlimited
export DEVICE_NUM=1
export RANK_SIZE=$DEVICE_NUM
export RANK_ID=0

if [ -d "eval" ];
then
    rm -rf ./eval
fi
mkdir ./eval
cp ../*.py ./eval
cp *.sh ./eval
cp -r ../src ./eval
cd ./eval || exit
env > env.log
echo "start evaluation for device $DEVICE_ID"
python eval_gpu.py --device_id=$DEVICE_ID --data_url=$PATH1 --train_url=$PATH2 \
                --ckpt_filename=$PATH3 --device_target="GPU" &> log &
cd ..
