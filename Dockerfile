FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r worker-requirements.txt

COPY handler.py ./

# RunPod Serverless looks for RUNPOD_HANDLER in env or defaults to 'handler'
ENV RUNPOD_HANDLER=handler.handler

CMD ["python", "-m", "runpod.serverless.worker"]