
FROM tensorflow/tensorflow:2.1.0-gpu-py3-jupyter

RUN apt-get update \
  && apt-get install --no-install-recommends -y \
     python3-openslide \
  && rm -rf /var/lib/apt/lists/*

ADD . /idc-pathomics-use-case-1

WORKDIR /idc-pathomics-use-case-1/src

EXPOSE 8888/tcp

ENTRYPOINT ["jupyter", "notebook", "--notebook-dir=/idc-pathomics-use-case-1/src", "--ip", "0.0.0.0", "--no-browser", "--allow-root"]
