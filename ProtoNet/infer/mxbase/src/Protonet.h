/**
 * Copyright 2021 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef MXBASE_BERTBASE_H
#define MXBASE_BERTBASE_H

#include <memory>
#include <utility>
#include <vector>
#include <string>
#include <map>
#include "MxBase/ModelInfer/ModelInferenceProcessor.h"
#include "MxBase/Tensor/TensorContext/TensorContext.h"

extern std::vector<double> g_inferCost;

struct InitParam {
    uint32_t deviceId;
    std::string labelPath;
    std::string modelPath;
};


class Protonet {
 public:
    APP_ERROR Init(const InitParam &initParam);
    APP_ERROR DeInit();
    APP_ERROR Inference(const std::vector<MxBase::TensorBase> &inputs, std::vector<MxBase::TensorBase> *outputs);
    APP_ERROR Process(const std::string &inferPath, const std::string &fileName);
 protected:
    APP_ERROR ReadTensorFromFile(const std::string &file, uint32_t *data, uint32_t size);
    APP_ERROR ReadInputTensor(const std::string &fileName, std::vector<MxBase::TensorBase> *inputs);
    APP_ERROR WriteResult(const std::string &imageFile, std::vector<MxBase::TensorBase> &outputs);


 private:
    std::shared_ptr<MxBase::ModelInferenceProcessor> model_;
    MxBase::ModelDesc modelDesc_ = {};
    std::vector<std::string> labelMap_ = {};
    uint32_t deviceId_ = 0;
    uint32_t classNum_ = 0;
};
#endif
