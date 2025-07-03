![MIT LICENSE](https://shields.io/badge/license-MIT-green)
![python 3.8](https://img.shields.io/badge/python-3.8-brightgreen)
# 🔥 Disentangling Writer and Character Styles for Handwriting Generation

 <p align='center'>
  <b>
    <a href="https://arxiv.org/abs/2303.14736">ArXiv</a>
    |
    <a href="https://github.com/dailenson/SDT/blob/master/static/Poster_SDT.pdf">Poster</a>
    | 
    <a href="https://youtu.be/mKbYLEwa4dI">Video</a>
    | 
    <a href="https://cvpr2023.thecvf.com/virtual/2023/poster/20954">Project</a>
  </b>
</p> 

## 📢 Introduction
- The proposed style-disentangled Transformer (SDT) generates online handwritings with conditional content and style. 
- Existing RNN-based methods mainly focus on capturing a person’s overall writing style, neglecting subtle style inconsistencies between characters written by the same person. In light of this, SDT disentangles the writer-wise and character-wise style representations from individual handwriting samples for enhancing imitation performance. 
- We extend SDT and introduce an offline-to-offline framework for improving the generation quality of offline Chinese handwritings.

# 🔥 SDT with connected dataset


## 🔨 Requirements
```
conda create -n sdt python=3.8 -y
conda activate sdt
# install all dependencies
conda env create -f environment.yml
```

## 📂 Folder Structure
  ```
  SDT/
  │
  ├── train.py - main script to start training
  ├── test.py - generate characters via trained model
  ├── evaluate.py - evaluation of generated samples
  │
  ├── configs/*.yml - holds configuration for training
  ├── parse_config.py - class to handle config file
  │
  ├── data_loader/ - anything about data loading goes here
  │   └── loader.py
  │
  ├── model_zoo/ - pre-trained content encoder model
  │
  ├── data/ - default directory for storing experimental datasets
  │
  ├── model/ - networks, models and losses
  │   ├── encoder.py
  │   ├── gmm.py
  │   ├── loss.py
  │   ├── model.py
  │   └── transformer.py
  │
  ├── saved/
  │   ├── models/ - trained models are saved here
  │   ├── tborad/ - tensorboard visualization
  │   └── samples/ - visualization samples in the training process
  │
  ├── trainer/ - trainers
  │   └── trainer.py
  │  
  └── utils/ - small utility functions
      ├── util.py
      └── logger.py - set log dir for tensorboard and logging output
  ```



