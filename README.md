# GIMP-ML-Hub
[![TravisCI](https://travis-ci.com/valgur/GIMP-ML-Hub.svg?branch=master)](https://travis-ci.com/github/valgur/GIMP-ML-Hub)

Machine Learning plugins for GIMP.

Forked from the [original version](https://github.com/kritiksoman/GIMP-ML) to improve the user experience in several aspects:
* The PyTorch models are packaged in [PyTorch Hub](https://pytorch.org/hub/) format and are only downloaded as needed. This allows new models to be added more seamlessly, without needing to re-download gigabytes of model weights.
* Models are run with Python 3, saving the needed effort to back-port them to Python 2.
* Fully automatic installation, that has been tested on all major operating systems and distros.
* Correct handling of alpha channels.
* Automatic conversion between RGB/grayscale as needed by the models.
* Results are always added to the same image instead of creating a new one. 
* Errors are now reported directly in the UI, not just in the command line.
* And many other smaller improvements.

The plugins [have been tested](https://travis-ci.com/github/valgur/GIMP-ML-Hub) with GIMP 2.10 on the following systems: <br>
* macOS Catalina 10.15.5
* ubuntu 18.04 LTS
* ubuntu 20.04 LTS
* Debian 10 (buster)
* Arch Linux
* Windows 10

# Installation Steps
1. Install [GIMP](https://www.gimp.org/downloads/). <br>
2. Clone this repository: `git clone https://github.com/kritiksoman/GIMP-ML.git` <br>
3. On Linux and MacOS run `./install.sh`.
4. On Windows:
      * Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
      * [Enable execution of Powershell scripts](https://superuser.com/a/106363/274408).
      * Run `install.ps1`.
5. Open GIMP and go to Preferences -> Folders -> Plug-ins, add the folder `GIMP-ML/plugins` and restart GIMP. <br>

# References
### MaskGAN
* Source: https://github.com/switchablenorms/CelebAMask-HQ
* Torch Hub fork: https://github.com/valgur/CelebAMask-HQ
* License:
   * [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode)
   * Copyright (C) 2017 NVIDIA Corporation. All rights reserved. 
   * Restricted to non-commercial research and educational purposes
* C.-H. Lee, Z. Liu, L. Wu, and P. Luo, “[MaskGAN: Towards Diverse and Interactive Facial Image Manipulation](http://arxiv.org/abs/1907.11922),”
in *IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, 2019.

### Face Parsing
* Source: https://github.com/zllrunning/face-parsing.PyTorch
* Torch Hub fork: https://github.com/valgur/face-parsing.PyTorch
* License: [MIT](https://github.com/zllrunning/face-parsing.PyTorch/blob/master/LICENSE)
* Based on BiSeNet:
   * https://github.com/CoinCheung/BiSeNet
   * License: [MIT](https://github.com/CoinCheung/BiSeNet/blob/master/LICENSE)
   * C. Yu, J. Wang, C. Peng, C. Gao, G. Yu, and N. Sang, “[BiSeNet: Bilateral segmentation network for
     real-time semantic segmentation](http://arxiv.org/abs/1808.00897),” in Lecture Notes in *Computer Science (including subseries Lecture Notes in 
     Artificial Intelligence and Lecture Notes in Bioinformatics)*, 2018, vol. 11217 LNCS, pp. 334–349.

### SRResNet
* Source: https://github.com/twtygqyy/pytorch-SRResNet
* Torch Hub fork: https://github.com/valgur/pytorch-SRResNet
* License: [MIT](https://github.com/twtygqyy/pytorch-SRResNet/blob/master/LICENSE)
* C. Ledig et al., “[Photo-Realistic Single Image Super-Resolution Using a Generative Adversarial Network](http://arxiv.org/abs/1609.04802),”
  in *2017 IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, 2017, pp. 105–114.

### DeblurGANv2
* Source: https://github.com/TAMU-VITA/DeblurGANv2
* Torch Hub fork: https://github.com/valgur/DeblurGANv2
* License: [BSD 3-clause](https://github.com/TAMU-VITA/DeblurGANv2/blob/master/LICENSE)
* O. Kupyn, T. Martyniuk, J. Wu, and Z. Wang, “[DeblurGAN-v2: Deblurring (Orders-of-Magnitude) Faster and Better](https://arxiv.org/abs/1908.03826),”
  in *2019 IEEE/CVF International Conference on Computer Vision (ICCV)*, 2019, pp. 8877–8886.

### MiDaS
* Source: https://github.com/intel-isl/MiDaS
* License: [MIT](https://github.com/intel-isl/MiDaS/blob/master/LICENSE), (c) 2019 Intel ISL (Intel Intelligent Systems Lab)
* R. Ranftl, K. Lasinger, D. Hafner, K. Schindler, and V. Koltun,
  “[Towards Robust Monocular Depth Estimation: Mixing Datasets for Zero-shot Cross-dataset Transfer](http://arxiv.org/abs/1907.01341),” 2019.

### Monodepth2
* Source: https://github.com/nianticlabs/monodepth2
* Torch Hub fork: https://github.com/valgur/monodepth2
* License:
   * See the [license file](https://github.com/nianticlabs/monodepth2/blob/master/LICENSE) for terms
   * Copyright © Niantic, Inc. 2019. Patent Pending. All rights reserved.
   * Non-commercial use only
* C. Godard, O. Mac Aodha, M. Firman, and G. Brostow, “[Digging Into Self-Supervised Monocular Depth Estimation](http://arxiv.org/abs/1806.01260),”
  in *2019 IEEE/CVF International Conference on Computer Vision (ICCV)*, 2019, pp. 3827–3837.

### Neural Colorization
* Source: https://github.com/zeruniverse/neural-colorization
* Torch Hub fork: https://github.com/valgur/neural-colorization
* License:
   * [GNU GPL 3.0](https://github.com/zeruniverse/neural-colorization/blob/pytorch/LICENSE) for personal or research use
   * Commercial use prohibited
   * Model weights released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
* Based on fast-neural-style:
   * https://github.com/jcjohnson/fast-neural-style
   * License:
      * Free for personal or research use
      * For commercial use please contact the authors
   * J. Johnson, A. Alahi, and L. Fei-Fei, “[Perceptual Losses for Real-Time Style Transfer and Super-Resolution](https://cs.stanford.edu/people/jcjohns/papers/eccv16/JohnsonECCV16.pdf),”
     in *Lecture Notes in Computer Science (including subseries Lecture Notes in Artificial Intelligence and Lecture Notes in Bioinformatics)*,
     vol. 9906 LNCS, 2016, pp. 694–711.

# Authors
* Martin Valgur ([valgur](https://github.com/valgur)) – this version
* Kritik Soman ([kritiksoman](https://github.com/kritiksoman)) – original GIMP-ML implementation

# License
MIT

Please note that additional license terms apply for each individual model. See the [references](#references) list for details.
Many of the models restrict usage to non-commercial or research purposes only.
