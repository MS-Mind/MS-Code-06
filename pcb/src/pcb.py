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
"""pcb.py"""

import mindspore.nn as nn
from mindspore.common.initializer import HeNormal, Normal, Constant
import mindspore.ops as ops

from src.model_utils.config import config
from src.resnet import resnet50


class PCB(nn.Cell):
    """PCB Model"""
    def __init__(self, num_classes):
        super(PCB, self).__init__()
        self.part = 6
        self.num_classes = num_classes
        resnet = resnet50(1000)
        self.base = resnet
        self.avgpool = ops.AvgPool(pad_mode="valid", kernel_size=(4, 8), strides=(4, 8))
        self.dropout = nn.Dropout(p=0.5)
        self.local_conv = nn.Conv2d(2048, 256, kernel_size=1, has_bias=False, \
pad_mode="valid", weight_init=HeNormal(mode="fan_out"))
        self.feat_bn2d = nn.BatchNorm2d(num_features=256)
        self.relu = ops.ReLU()
        self.expandDims = ops.ExpandDims()
        self.split = ops.Split(2, 6)
        # define 6 classifiers
        self.instance0 = nn.Dense(256, self.num_classes, weight_init=Normal(sigma=0.001), bias_init=Constant(0))
        self.instance1 = nn.Dense(256, self.num_classes, weight_init=Normal(sigma=0.001), bias_init=Constant(0))
        self.instance2 = nn.Dense(256, self.num_classes, weight_init=Normal(sigma=0.001), bias_init=Constant(0))
        self.instance3 = nn.Dense(256, self.num_classes, weight_init=Normal(sigma=0.001), bias_init=Constant(0))
        self.instance4 = nn.Dense(256, self.num_classes, weight_init=Normal(sigma=0.001), bias_init=Constant(0))
        self.instance5 = nn.Dense(256, self.num_classes, weight_init=Normal(sigma=0.001), bias_init=Constant(0))

    def construct(self, x):
        """Forward propagation"""
        x = self.base.conv1(x)
        x = self.base.bn1(x)
        x = self.base.relu(x)
        x = self.base.pad(x)
        x = self.base.maxpool(x)
        x = self.base.layer1(x)
        x = self.base.layer2(x)
        x = self.base.layer3(x)
        x = self.base.layer4(x)
        x = self.avgpool(x)
        g_feature = x / (self.expandDims(ops.norm(x, dim=1), 1)).expand_as(x)
        if self.training:
            x = self.dropout(x)
        x = self.local_conv(x)
        h_feature = x / (self.expandDims(ops.norm(x, dim=1), 1)).expand_as(x)
        x = self.feat_bn2d(x)
        x = self.relu(x)
        x = self.split(x)
        x0 = x[0].view(x[0].shape[0], -1)
        x1 = x[1].view(x[1].shape[0], -1)
        x2 = x[2].view(x[2].shape[0], -1)
        x3 = x[3].view(x[3].shape[0], -1)
        x4 = x[4].view(x[4].shape[0], -1)
        x5 = x[5].view(x[5].shape[0], -1)
        c0 = self.instance0(x0)
        c1 = self.instance1(x1)
        c2 = self.instance2(x2)
        c3 = self.instance3(x3)
        c4 = self.instance4(x4)
        c5 = self.instance5(x5)
        return (c0, c1, c2, c3, c4, c5), g_feature, h_feature


class NetWithLossCell(nn.Cell):
    """Wrap loss function in network"""
    def __init__(self, network):
        super(NetWithLossCell, self).__init__()
        self.network = network
        self.loss_fn = nn.SoftmaxCrossEntropyWithLogits(sparse=True, reduction="mean")

    def construct(self, imgs, fids, pids, camids):
        """Forward propagation"""
        inputs, targets = imgs, pids
        (c0, c1, c2, c3, c4, c5), _, _ = self.network(inputs)
        loss0 = self.loss_fn(c0, targets)
        loss1 = self.loss_fn(c1, targets)
        loss2 = self.loss_fn(c2, targets)
        loss3 = self.loss_fn(c3, targets)
        loss4 = self.loss_fn(c4, targets)
        loss5 = self.loss_fn(c5, targets)
        loss = (loss0 + loss1 + loss2 + loss3 + loss4 + loss5)
        return loss


#for 310 infer
use_G_feature = config.use_G_feature


class PCB_infer(nn.Cell):
    """PCB for inference with classifiers removed"""
    def __init__(self):
        super(PCB_infer, self).__init__()
        self.part = 6
        resnet = resnet50(1000)
        self.base = resnet
        self.avgpool = ops.AvgPool(pad_mode="valid", kernel_size=(4, 8), strides=(4, 8))
        self.local_conv = nn.Conv2d(2048, 256, kernel_size=1, has_bias=False, \
pad_mode="valid", weight_init=HeNormal(mode="fan_out"))
        self.feat_bn2d = nn.BatchNorm2d(num_features=256)
        self.relu = ops.ReLU()
        self.expandDims = ops.ExpandDims()

    def construct(self, x):
        """Forward propagation"""
        x = self.base.conv1(x)
        x = self.base.bn1(x)
        x = self.base.relu(x)
        x = self.base.pad(x)
        x = self.base.maxpool(x)
        x = self.base.layer1(x)
        x = self.base.layer2(x)
        x = self.base.layer3(x)
        x = self.base.layer4(x)
        x = self.avgpool(x)
        g_feature = x / (self.expandDims(ops.norm(x, dim=1), 1)).expand_as(x)
        x = self.local_conv(x)
        h_feature = x / (self.expandDims(ops.norm(x, dim=1), 1)).expand_as(x)
        if use_G_feature:
            return g_feature
        return h_feature
