# Optional image build. docker-compose.yml does not need this —
# it runs the official python:3.12-alpine image against these files.
FROM python:3.12-alpine
WORKDIR /app
COPY server.py index.html ./
RUN mkdir -p /data
ENV INVOICEFLOW_HOST=0.0.0.0
ENV INVOICEFLOW_PORT=8765
ENV INVOICEFLOW_DATA=/data/invoiceflow-data.json
EXPOSE 8765
CMD ["python3", "server.py", "--lan", "--data", "/data/invoiceflow-data.json"]
