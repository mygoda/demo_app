FROM bitnami/python:3.8
RUN apt update && apt-get install libmariadb-dev-compat libmariadb-dev -y
RUN mkdir /code
ADD . /code
WORKDIR /code
RUN pip install -r requirement.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
CMD ["/bin/sh", "-c", "python app.py"]
