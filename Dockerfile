
FROM tensorflow/tensorflow:2.1.0-gpu-py3-jupyter

ADD requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

VOLUME ["/input_data", "/output_data"]

ADD . /idc-pathomics-use-case-1

WORKDIR /idc-pathomics-use-case-1

EXPOSE 8888/tcp

ENTRYPOINT ["jupyter", "notebook", "--notebook-dir=/idc-pathomics-use-case-1/src", "--ip", "0.0.0.0", "--no-browser", "--allow-root"]
