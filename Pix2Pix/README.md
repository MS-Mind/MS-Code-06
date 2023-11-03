# Contents

- [Contents](#contents)
- [Pix2Pix Description](#pix2pix-description)
- [Model Architecture](#model-architecture)
- [Dataset](#dataset)
- [Environment Requirements](#environment-requirements)
    - [Dependences](#dependences)
- [Script Description](#script-description)
    - [Script and Sample Code](#script-and-sample-code)
    - [Script Parameters](#script-parameters)
    - [Training](#training)
    - [Evaluation](#evaluation)
    - [Infer](#infer)
    - [Onnx export](#onnx-export)
    - [Onnx infer](#onnx-infer)
- [Model Description](#model-description)
    - [Performance](#performance)
        - [Training Performance on single device](#training-performance-on-single-device)
        - [Distributed Training Performance](#distributed-training-performance)
        - [Evaluation Performance](#evaluation-performance)
- [ModelZoo Homepage](#modelzoo-homepage)

# [Pix2Pix Description](#contents)

Many problems in image processing, computer graphics, and computer vision can be posed as “translating” an input image into a corresponding output image, each of these tasks has been tackled with separate, special-purpose machinery, despite the fact that the setting is always the same: predict pixels from pixels.
Our goal in this paper is to develop a common framework for all these problems. Pix2pix model is a conditional GAN, which includes two modules--generator and discriminator. This model transforms an input image into a corresponding output image. The essence of the model is the mapping from pixel to pixel.

[Paper](https://arxiv.org/abs/1611.07004): Phillip Isola, Jun-Yan Zhu, Tinghui Zhou, and Alexei A. Efros. "Image-to-Image Translation with Conditional Adversarial Networks", in CVPR 2017.

![Pix2Pix Imgs](imgs/Pix2Pix-examples.jpg)

# [Model Architecture](#contents)

The Pix2Pix contains a generation network and a discriminant networks.In the generator part, the model can be any pixel to pixel mapping network (in the raw paper, the author proposed to use Unet). In the discriminator part, a patch GAN is used to judge whether each N*N patches is fake or true, thus can improve the reality of the generated image.

**Generator(Unet-Based) architectures:**

Encoder:

C64-C128-C256-C512-C512-C512-C512-C512

Decoder:

CD512-CD1024-CD1024-C1024-C1024-C512-C256-C128

**Discriminator(70 × 70 discriminator) architectures:**

C64-C128-C256-C512

**Note:** Let Ck denote a Convolution-BatchNorm-ReLU layer with k filters. CDk denotes a Convolution-BatchNorm-Dropout-ReLU layer with a dropout rate of 50%.

# [Dataset](#contents)

Dataset_1 used: [facades](http://efrosgans.eecs.berkeley.edu/pix2pix/datasets/facades.tar.gz)

```text
    Dataset size: 29M, 606 images
                  400 train images
                  100 validation images
                  106 test images
    Data format：.jpg images
```

Dataset_2 used: [maps](http://efrosgans.eecs.berkeley.edu/pix2pix/datasets/maps.tar.gz)

```text
    Dataset size: 239M, 2194 images
                  1096 train images
                  1098 validation images
    Data format：.jpg images
```

**Note:** We provide data/download_Pix2Pix_dataset.sh to download the datasets.

Download facades dataset

```shell
bash data/download_Pix2Pix_dataset.sh facades
```

Download maps dataset

```shell
bash data/download_Pix2Pix_dataset.sh maps
```

# [Environment Requirements](#contents)

- Hardware（Ascend）
    - Prepare hardware environment with Ascend processor.
- Framework
    - [MindSpore](https://www.mindspore.cn/install/en)
- For more information, please check the resources below：
    - [MindSpore tutorials](https://www.mindspore.cn/tutorials/en/master/index.html)
    - [MindSpore Python API](https://www.mindspore.cn/docs/en/master/index.html)

## [Dependences](#contents)

- Python==3.8.5
- Mindspore==1.2

# [Script Description](#contents)

## [Script and Sample Code](#contents)

The entire code structure is as following:

```text
.Pix2Pix
├─ README.md                           # descriptions about Pix2Pix
├─ data
  └─download_Pix2Pix_dataset.sh        # download dataset
├── scripts
  └─run_infer_310.sh                   # launch ascend 310 inference
  └─run_distribute_train_ascend.sh     # launch ascend training(8 pcs)
  └─run_eval.sh                        # launch evaluation
  └─run_train.sh                       # launch gpu/ascend training(1 pcs)
  └─run_distribute_train_gpu.sh        # launch gpu training(8 pcs)
  └─run_infer_onnx.sh                  # launch onnx infer
├─ imgs
  └─Pix2Pix-examples.jpg               # Pix2Pix Imgs
├─ src
  ├─ __init__.py                       # init file
  ├─ dataset
    ├─ __init__.py                     # init file
    ├─ pix2pix_dataset.py              # create pix2pix dataset
  ├─ models
    ├─ __init__.py                     # init file
    ├─ discriminator_model.py          # define discriminator model——Patch GAN
    ├─ generator_model.py              # define generator model——Unet-based Generator
    ├─ init_w.py                       # initialize network weights
    ├─ loss.py                         # define losses
    └─ pix2pix.py                      # define Pix2Pix model
  └─ utils
    ├─ __init__.py                     # init file
    ├─ config.py                       # parse args
    ├─ tools.py                        # tools for Pix2Pix model
    ├─ device_adapter.py               # Get cloud ID
    ├─ local_adapter.py                # Get local ID
    ├─ moxing_adapter.py               # Parameter processing
├─ eval.py                             # evaluate Pix2Pix Model
├─ infer_onnx.py                       # Pix2Pix onnx inference
├─ train.py                            # train script
├─ requirements.txt                    # requirements file
└─ export.py                           # export mindir and air script
```

## [Script Parameters](#contents)

Major parameters in train.py and config.py as follows:

```text
"device_target": Ascend                     # run platform, only support Ascend.
"device_num": 1                             # device num, default is 1.
"device_id": 0                              # device id, default is 0.
"save_graphs": False                        # whether save graphs, default is False.
"init_type": normal                         # network initialization, default is normal.
"init_gain": 0.02                           # scaling factor for normal, xavier and orthogonal, default is 0.02.
"load_size": 286                            # scale images to this size, default is 286.
"batch_size": 1                             # batch_size, default is 1.
"LAMBDA_Dis": 0.5                           # weight for Discriminator Loss, default is 0.5.
"LAMBDA_GAN": 1                             # weight for GAN Loss, default is 1.
"LAMBDA_L1": 100                            # weight for L1 Loss, default is 100.
"beta1": 0.5                                # adam beta1, default is 0.5.
"beta2": 0.999                              # adam beta2, default is 0.999.
"lr": 0.0002                                # the initial learning rate, default is 0.0002.
"lr_policy": linear                         # learning rate policy, default is linear.
"epoch_num": 200                            # epoch number for training, default is 200.
"n_epochs": 100                             # number of epochs with the initial learning rate, default is 100.
"n_epochs_decay": 100                       # number of epochs with the dynamic learning rate, default is 100.
"dataset_size": 400                         # for Facade_dataset,the number is 400; for Maps_dataset,the number is 1096.
"train_data_dir": None                      # the file path of input data during training.
"val_data_dir": None                        # the file path of input data during validating.
"onnx_infer_data_dir": ./data/facades/val/  # the file path of input data during onnx infer.
"train_fakeimg_dir": ./results/fake_img/    # during training, the file path of stored fake img.
"loss_show_dir": ./results/loss_show        # during training, the file path of stored loss img.
"ckpt_dir": ./results/ckpt                  # during training, the file path of stored CKPT.
"ckpt": None                                # during validating, the file path of the CKPT used.
"onnx_path": None                           # during onnx infer, the file path of the ONNX used.
"predict_dir": ./results/predict/           # during validating, the file path of Generated images.
"onnx_infer_dir": ./results/onnx_infer/     # during onnx infer, the file path of Generated images.
```

## [Training](#contents)

- running on Ascend with default parameters

```shell
python train.py --device_target=[Ascend] --device_id=[0]
```

- running distributed trainning on Ascend with fixed parameters

```shell
bash scripts/run_distribute_train_ascend.sh [RANK_TABLE_FILE] [DATASET_PATH]
```

- running on GPU with fixed parameters

```shell
python train.py --device_target=[GPU] --device_id=[0]
# OR
bash scripts/run_train.sh [DEVICE_TARGET] [DEVICE_ID]
```

- running distributed trainning on GPU with fixed parameters

```shell
bash scripts/run_distribute_train_gpu.sh [DATASET_PATH] [DATASET_NAME]
```

## [Evaluation](#contents)

- running on Ascend

```shell
python eval.py --device_target=[Ascend] --device_id=[0] --val_data_dir=[./data/facades/test] --ckpt=[./results/ckpt/Generator_200.ckpt] --pad_mode=REFLECT
# OR
bash scripts/run_eval.sh [DEVICE_TARGET] [DEVICE_ID] [VAL_DATA_DIR] [CKPT_PATH]
```

- running on GPU

```shell
python eval.py --device_target=[GPU] --device_id=[0] --val_data_dir=[./data/facades/test] --ckpt=[./train/results/ckpt/Generator_200.ckpt]
# OR
bash scripts/run_eval.sh [DEVICE_TARGET] [DEVICE_ID] [VAL_DATA_DIR] [CKPT_PATH]
```

**Note:**: Before training and evaluating, create folders like "./results/...". Then you will get the results as following in "./results/predict".

## [Infer](#contents)

**Before inference, please refer to [MindSpore Inference with C++ Deployment Guide](https://gitee.com/mindspore/models/blob/master/utils/cpp_infer/README.md) to set environment variables.**

```shell
bash run_infer_cpp.sh [MINDIR_PATH] [DATASET_PATH] [NEED_PREPROCESS] [DEVICE_TARGET] [DEVICE_ID]
```

## [Onnx export](#contents)

```shell
python export.py --ckpt=[/path/pix2pix.ckpt] --device_target=[GPU] --device_id=[0] --file_format=ONNX
```

## [Onnx infer](#contents)

```shell
python infer_onnx.py --device_target=[GPU] --device_id=[0] --onnx_infer_data_dir=[/path/data] --onnx_path=[/path/pix2pix.onnx]
OR
bash scripts/run_infer_onnx.sh [DEVICE_TARGET] [DEVICE_ID] [ONNX_INFER_DATA_DIR] [ONNX_PATH]
```

# [Model Description](#contents)

## [Performance](#contents)

### Training Performance on single device

| Parameters                 | single Ascend                                            | single GPU                                                         |
| -------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------- |
| Model Version              | Pix2Pix                                                    | Pix2Pix                                                          |
| Resource                   | Ascend 910                                               | PCIE V100-32G                                                      |
| MindSpore Version          | 1.2                                                         | 1.3.0                                                           |
| Dataset                    | facades                                                  | facades                                                |
| Training Parameters        | epoch=200, steps=400, batch_size=1, lr=0.0002               | epoch=200, steps=400, batch_size=1, lr=0.0002, pad_mode=REFLECT |
| Optimizer                  | Adam                                                        | Adam                                                            |
| Loss Function              | SigmoidCrossEntropyWithLogits Loss & L1 Loss                                   | SigmoidCrossEntropyWithLogits Loss & L1 Loss |
| outputs                    | probability                                                 | probability                                                     |
| Speed                      | 1pc(Ascend): 10 ms/step                                  | 1pc(GPU): 40 ms/step                                     |
| Total time                 | 1pc(Ascend): 0.3h                                        | 1pc(GPU): 0.8 h                                     |
| Checkpoint for Fine tuning | 207M (.ckpt file)                                            | 207M (.ckpt file)                                              |

| Parameters                 | single Ascend                                            | single GPU                                                         |
| -------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------- |
| Model Version              | Pix2Pix                                                    | Pix2Pix                                                          |
| Resource                   | Ascend 910                                               |
| MindSpore Version          | 1.2                                                         | 1.3.0                                                           |
| Dataset                    | maps                                                     | maps                                                               |
| Training Parameters        | epoch=200, steps=1096, batch_size=1, lr=0.0002              | epoch=200, steps=400, batch_size=1, lr=0.0002, pad_mode=REFLECT |
| Optimizer                  | Adam                                                        | Adam                                                            |
| Loss Function              | SigmoidCrossEntropyWithLogits Loss & L1 Loss                                   | SigmoidCrossEntropyWithLogits Loss & L1 Loss |
| outputs                    | probability                                                 | probability                                                     |
| Speed                      | 1pc(Ascend): 20 ms/step                                  | 1pc(GPU): 90 ms/step                                     |
| Total time                 | 1pc(Ascend): 1.58h                                       | 1pc(GPU): 3.3h                                     |
| Checkpoint for Fine tuning | 207M (.ckpt file)                                            | 207M (.ckpt file)                                              |

### Distributed Training Performance

| Parameters                 | Ascend    (8pcs)                                        | GPU   (8pcs)                                                      |
| -------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------- |
| Model Version              | Pix2Pix                                                    | Pix2Pix                                                          |
| Resource                   | Ascend 910                                               | PCIE V100-32G                                                      |
| MindSpore Version          | 1.4.1                                                         | 1.3.0                                                           |
| Dataset                    | facades                                                  | facades                                                |
| Training Parameters        | epoch=200, steps=400, batch_size=1, lr=0.0002               | epoch=200, steps=400, batch_size=1, lr=0.0002, pad_mode=REFLECT |
| Optimizer                  | Adam                                                        | Adam                                                            |
| Loss Function              | SigmoidCrossEntropyWithLogits Loss & L1 Loss                                   | SigmoidCrossEntropyWithLogits Loss & L1 Loss |
| outputs                    | probability                                                 | probability                                                     |
| Speed                      | 8pc(Ascend): 15 ms/step                                  | 8pc(GPU): 30 ms/step                                     |
| Total time                 | 8pc(Ascend): 0.5h                                        | 8pc(GPU): 1 h                                     |
| Checkpoint for Fine tuning | 207M (.ckpt file)                                            | 207M (.ckpt file)                                              |

| Parameters                 | Ascend    (8pcs)                                            | GPU   (8pcs)                                                         |
| -------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------- |
| Model Version              | Pix2Pix                                                    | Pix2Pix                                                          |
| Resource                   | Ascend 910                                               | PCIE V100-32G                                                    |
| MindSpore Version          | 1.4.1                                                         | 1.3.0                                                           |
| Dataset                    | maps                                                     | maps                                                               |
| Training Parameters        | epoch=200, steps=1096, batch_size=1, lr=0.0002              | epoch=200, steps=400, batch_size=1, lr=0.0002, pad_mode=REFLECT |
| Optimizer                  | Adam                                                        | Adam                                                            |
| Loss Function              | SigmoidCross55EntropyWithLogits Loss & L1 Loss                                   | SigmoidCrossEntropyWithLogits Loss & L1 Loss |
| outputs                    | probability                                                 | probability                                                     |
| Speed                      | 8pc(Ascend): 20 ms/step                                  | 8pc(GPU): 40 ms/step                                     |
| Total time                 | 8pc(Ascend): 1.2h                                       | 8pc(GPU): 2.8h                                     |
| Checkpoint for Fine tuning | 207M (.ckpt file)                                            | 207M (.ckpt file)                                              |

### Evaluation Performance

| Parameters          | single Ascend               | single GPU                  |
| ------------------- | --------------------------- | --------------------------- |
| Model Version       | Pix2Pix                     | Pix2Pix                     |
| Resource            | Ascend 910                  | PCIE V100-32G               |
| MindSpore Version   | 1.2                         | 1.3.0                       |
| Dataset             | facades / maps              | facades / maps              |
| batch_size          | 1                           | 1                           |
| outputs             | probability                 | probability                 |

# [ModelZoo Homepage](#contents)

Please check the official [homepage](https://gitee.com/mindspore/models).
