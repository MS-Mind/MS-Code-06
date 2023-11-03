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
if [ $# != 1 ]; then
  echo "Usage: bash run_eval_ascend.sh [device_id]"
  exit 1
fi
export DEVICE_ID=$1

DIR="$( cd "$( dirname "$0"  )" && pwd  )"

ulimit -n 65530

cd $DIR/../ || exit
nohup python eval.py --device_target=Ascend > eval_ascend_log.txt 2>&1 &
echo 'Validation task has been started successfully!'
echo 'Please check the log at eval_ascend_log.txt'
