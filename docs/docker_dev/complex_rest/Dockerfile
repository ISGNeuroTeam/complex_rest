FROM python:3.9.7
ENV PYTHONUNBUFFERED=1

ENV DATABASE=postgres
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV REST_CONF=/complex_rest/docs/docker_dev/complex_rest/rest.conf
ENV PYTHONPATH=/complex_rest/complex_rest

RUN mkdir /complex_rest
WORKDIR /complex_rest
COPY requirements.txt /complex_rest/
RUN pip install --no-cache-dir  -r requirements.txt
COPY complex_rest /complex_rest/
COPY docs /complex_rest/

ENTRYPOINT ["/complex_rest/docs/docker_dev/complex_rest/entrypoint.sh"]
CMD ["/complex_rest/docs/docker_dev/complex_rest/start.sh"]
EXPOSE 8080