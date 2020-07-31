Introductory videos Genomic Data Commons: <https://gdc.cancer.gov/support>
Openslide: <https://developer.ibm.com/articles/an-automatic-method-to-identify-tissues-from-big-whole-slide-images-pt1/>, <https://openslide.org/api/python/>

Code structure: 

```bash
├── src
│   ├── 00_preprocessing
│   │   ├── 00_1
│   │   ├── ...
│   │   ├── README.md
│   ├── 01_training
│   │   ├── 01_1
│   │   ├── ...
│   │   ├── README.md
│   ├── 02_testing
│   │   ├── 02_1
│   │   ├── ...
│   │   ├── README.md
│   ├── 03_evaluation 
│   │   ├── 03_01
│   │   ├── ...
│   │   ├── README.md
│   ├── README/Documentation.md
├── docker
│   ├── buildDockerImage.sh
│   ├── Dockerfile
│   ├── setupAndRunInsideDocker.sh
├── runLocallyInDocker
│   ├── _buildImageAndRunLocallyInDocker.sh
├── runOnCluster
│   ├── _buildImageAndRunOnCluster.sh
├── README.md

```
