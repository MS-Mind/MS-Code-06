# Copyright 2020-2022 Huawei Technologies Co., Ltd
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


import time

import mindspore.nn as nn
from mindspore.train.callback import Callback

__all__ = ['LossCallBack', 'WithLossCell']

class AverageMeter():
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

class LossCallBack(Callback):
    """
    Monitor the loss in training.

    If the loss is NAN or INF terminating training.

    Note:
        If per_print_times is 0 do not print loss.

    Args:
        per_print_times (int): Print loss every times. Default: 1.
    """
    def __init__(self, per_print_times=1):
        super(LossCallBack, self).__init__()
        if not isinstance(per_print_times, int) or per_print_times < 0:
            raise ValueError("print_step must be int and >= 0.")
        self._per_print_times = per_print_times
        self.loss_avg = AverageMeter()

    def step_end(self, run_context):
        cb_params = run_context.original_args()
        loss = cb_params.net_outputs
        if isinstance(loss, tuple):
            overflow = loss[1].asnumpy()
            if overflow:
                print("overflow!!!")
            loss = loss[0]
        loss = loss.asnumpy()
        cur_step_in_epoch = (cb_params.cur_step_num - 1) % cb_params.batch_num + 1
        cur_num = cb_params.cur_step_num

        if cur_step_in_epoch == 1:
            self.loss_avg = AverageMeter()

        self.loss_avg.update(loss)

        if self._per_print_times != 0 and cur_num % self._per_print_times == 0:
            loss_log = "time: %s, epoch: %s, step: %s, loss is %s" % (
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                cb_params.cur_epoch_num,
                cur_step_in_epoch,
                self.loss_avg.avg)
            print(loss_log)
            loss_file = open("./loss.log", "a+")
            loss_file.write(loss_log)
            loss_file.write("\n")
            loss_file.close()

class WithLossCell(nn.Cell):
    """
    Wrap the network with loss function to compute loss.

    Args:
        backbone (Cell): The target network to wrap.
        loss_fn (Cell): The loss function used to compute loss.
    """
    def __init__(self, backbone, loss_fn):
        super(WithLossCell, self).__init__(auto_prefix=False)
        self._backbone = backbone
        self._loss_fn = loss_fn

    def construct(self, img, gt_text, gt_kernels, training_mask):
        model_predict = self._backbone(img)
        return self._loss_fn(model_predict, gt_text, gt_kernels, training_mask)

    @property
    def backbone_network(self):
        """
        Get the backbone network.

        Returns:
            Cell, return backbone network.
        """
        return self._backbone
