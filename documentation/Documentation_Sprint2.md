# Documentation
## First sprint (until 27/07/2020)
see LiteratureResearch.md and ImplementationStrategy.md

## Second sprint (until 24/08/2020)

Introductory videos Genomic Data Commons: <https://gdc.cancer.gov/support>

Openslide pages: 
    * <https://developer.ibm.com/articles/an-automatic-method-to-identify-tissues-from-big-whole-slide-images-pt1/>, 
    * <https://openslide.org/api/python/>

Notes on Coudray's code: 
* they adapted code from an openslide example: <https://github.com/openslide/openslide-python/blob/master/examples/deepzoom/deepzoom_tile.py>
* they use the TFRecord datastructure which is a binary format and seems to significantly reduce processing time: https://medium.com/mostly-ai/tensorflow-records-what-they-are-and-how-to-use-them-c46bc4bbb564

Questions: 
* what about taking code from coudray, openslide, i.e. third party code??

Notes for me: 
* <https://stackabuse.com/pythons-classmethod-and-staticmethod-explained/>


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
