# Documentation
## First sprint (until 27/07/2020)
see LiteratureResearch.md and ImplementationStrategy.md

## Second sprint (until 31/08/2020)

Introductory videos Genomic Data Commons: <https://gdc.cancer.gov/support>

Openslide pages: 
    * <https://developer.ibm.com/articles/an-automatic-method-to-identify-tissues-from-big-whole-slide-images-pt1/>, 
    * <https://openslide.org/api/python/>

Notes on Coudray's code: 
* they adapted code from an openslide example: <https://github.com/openslide/openslide-python/blob/master/examples/deepzoom/deepzoom_tile.py>
* they use the TFRecord datastructure which is a binary format and seems to significantly reduce processing time: https://medium.com/mostly-ai/tensorflow-records-what-they-are-and-how-to-use-them-c46bc4bbb564

Network: 
* Inception v3: Christian Szegedy, Vincent Vanhoucke, Sergey Ioffe, Jonathon Shlens, Zbigniew Wojna. "Rethinking the Inception Architecture for Computer Vision" http://arxiv.org/abs/1512.00567 (cited by Coudray)
* Inception v3 Github: https://github.com/tensorflow/models/tree/f87a58cd96d45de73c9a8330a06b2ab56749a7fa/research/inception#adjusting-memory-demands (not up to date, however link to updated page leads to nothing...)
* Network to be trained from scratch: bazel build inception/imagenet_train
* Pre-trained: bazel build inception/imagenet_train 
plus curl -O http://download.tensorflow.org/models/image/imagenet/inception-v3-2016-03-01.tar.gz
> Inception v3 also available via Keras: https://keras.io/api/applications/inceptionv3/ but I am not sure whether the weights are exactly the same from 2016-03-01. 

ToDo: 
* check advantage of using logits in the loss function
* ensure that the top layers are the same in Coudray Code
* genetic mutations 