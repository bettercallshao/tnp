FROM gcr.io/cloud-builders/gcloud

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-pip && \
    pip3 install setuptools wheel

WORKDIR /tnp
COPY . .
RUN pip3 install .
ENTRYPOINT ["tnp"]
