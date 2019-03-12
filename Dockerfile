# SSE (Simple Search Engine) 도커 이미지 파일
# - Flask 이용한 검색엔진 RESTful API 테스트 위한 도커 이미지
# - SSE (Simple Search Engine) 이라는 이름으로 지정
FROM python:3

ENV PYTHONPATH=/sse
ENV FLASK_APP=main.py

COPY ./src/ /sse
COPY ./scripts/requirements.txt /sse
COPY ./scripts/adjustMapping.sh /sse
COPY ./scripts/prepare.sh /sse
COPY ./scripts/runner.sh /sse/runner.sh

ENV SSE_HOST=elasticsearch_sse:9200

# 의존성 패키지 설치
RUN pip install --no-cache-dir --quiet -r /sse/requirements.txt

ENTRYPOINT ["/sse/runner.sh"]
CMD ["sse"]

EXPOSE 5000
EXPOSE 80
