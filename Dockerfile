FROM bitnami/python:3.8
RUN mkdir /code
ADD . /code
WORKDIR /code
RUN pip install -r requirement.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
CMD ["/bin/sh", "-c", "python app.py"]
