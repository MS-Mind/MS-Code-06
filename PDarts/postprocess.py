# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# less required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""postprocess for 310 inference"""
import os
import argparse
import numpy as np
from mindspore.nn import Top1CategoricalAccuracy

batch_size = 1
parser = argparse.ArgumentParser(description="postprocess")
label_path = "./preprocess_Result/cifar10_label_ids.npy"
parser.add_argument("--result_dir", type=str, default="./result_Files", help="result files path.")
parser.add_argument("--label_dir", type=str, default=label_path, help="image file path.")
args = parser.parse_args()
if __name__ == '__main__':
    top1_acc = Top1CategoricalAccuracy()
    rst_path = args.result_dir
    labels = np.load(args.label_dir, allow_pickle=True)
    for idx, label in enumerate(labels):
        f_name = os.path.join(rst_path, "pdarts_data_bs" + str(batch_size) + "_" + str(idx) + "_0.bin")
        pred = np.fromfile(f_name, np.float32)
        pred = pred.reshape(batch_size, int(pred.shape[0] / batch_size))
        top1_acc.update(pred, labels[idx])
    print("acc: ", top1_acc.eval())
