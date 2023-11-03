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
"""export checkpoint file into AIR MINDIR ONNX models"""
import numpy as np

import mindspore as ms
from mindspore import Tensor, load_checkpoint, load_param_into_net, export, context

from src.proxylessnas_mobile import proxylessnas_mobile
from src.model_utils.config import config

if __name__ == '__main__':
    context.set_context(mode=context.GRAPH_MODE, device_target=config.device_target, save_graphs=False)
    if config.device_target == "Ascend" or config.device_target == "GPU":
        context.set_context(device_id=config.device_id)

    net = proxylessnas_mobile(num_classes=config.num_classes)
    param_dict = load_checkpoint(config.checkpoint)
    load_param_into_net(net, param_dict)

    input_data = Tensor(np.ones([1, 3, 224, 224]), ms.float32)
    export(net, input_data, file_name=config.file_name, file_format=config.file_format)
