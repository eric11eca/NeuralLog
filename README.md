
# NeuralLog: Natural Language Inference with Joint Neural and Logical Reasoning
[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/neurallog-natural-language-inference-with/natural-language-inference-on-med)](https://paperswithcode.com/sota/natural-language-inference-on-med?p=neurallog-natural-language-inference-with)
[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/neurallog-natural-language-inference-with/natural-language-inference-on-sick)](https://paperswithcode.com/sota/natural-language-inference-on-sick?p=neurallog-natural-language-inference-with)

Deep learning (DL) based language models achieve high performance on various benchmarks for Natural Language Inference (NLI). And at this time, symbolic approaches to NLI are receiving less attention. Both approaches (symbolic and DL) have their advantages and weaknesses. However, currently, no method combines them in a system to solve the task of NLI. To merge symbolic and deep learning methods, we propose an inference framework called NeuralLog, which utilizes both a monotonicity-based logical inference engine and a neural network language model for phrase alignment. Our framework models the NLI task as a classic search problem and uses the beam search algorithm to search for optimal inference paths. Experiments show that our joint logic and neural inference system improves accuracy on the NLI task and can achieve state-of-art accuracy on the SICK and MED datasets.

The following publications are integrated in this framework:
- [NeuralLog: Natural Language Inference with Joint Neural and Logical Reasoning](https://arxiv.org/abs/2105.14167) (*SEM2021 @ ACL2021)
- [Monotonicity Marking from Universal Dependency Trees](https://arxiv.org/abs/1908.10084) (IWCS 2021)

## Installation
The recoomanded environment include **Python 3.6** or higher , **[Stanza v1.2.0](https://github.com/stanfordnlp/stanza)** or higher, and **[ImageMagick v7.0.11](https://imagemagick.org/script/download.php). The code does **not** work with Python 2.7.

**Clone the repository**
```
git clone https://github.com/eric11eca/NeuralLog.git
```

## Getting Started

First download a pretrained model from [Google Drive](https://drive.google.com/drive/folders/1XHCHA2inUs-1CfCXobFL0Feaw-eEsO5Y?usp=sharing). Replace the Stanza defalut depparse model with this pretrained version. The Stanza model path is: 
````
C:\Users\$your_user_name$\stanza_resources\en\
````
Then open UdeoLog.ipynb

## Pre-Trained UD Parser Models

We provide two [UD Parser Models](https://drive.google.com/drive/folders/1XHCHA2inUs-1CfCXobFL0Feaw-eEsO5Y?usp=sharing) for English. Some models are general purpose models, while others produce embeddings for specific use cases. Pre-trained models can be loaded by just passing the model name: `SentenceTransformer('model_name')`.

## Training
For training new UD parser models, see [Stanza's training dcumentation](https://stanfordnlp.github.io/stanza/training.html#setting-environment-variables) for an introduction how to train your own UD parser. 

## Citing & Authors
If you find this repository helpful, feel free to cite our publication [Monotonicity Marking from Universal Dependency Trees](https://arxiv.org/abs/1908.10084):
```bibtex 
@misc{chen2021neurallog,
      title={NeuralLog: Natural Language Inference with Joint Neural and Logical Reasoning}, 
      author={Zeming Chen and Qiyue Gao and Lawrence S. Moss},
      year={2021},
      eprint={2105.14167},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

Contact person: Zeming Chen, [chenz16@rose-hulman.edu](mailto:chenz16@rose-hulman.edu)
Don't hesitate to send us an e-mail or report an issue, if something is broken or if you have further questions.

> This repository contains experimental software and is published for the sole purpose of giving additional background details on the respective publication.
