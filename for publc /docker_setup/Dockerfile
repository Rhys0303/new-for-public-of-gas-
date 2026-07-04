FROM ultralytics/ultralytics:latest-arm64

RUN pip uninstall torch torchvision -y
RUN pip install torch==2.5.1 torchvision
RUN pip install flask

WORKDIR /app

COPY best.pt /app/best.pt
COPY templates/ /app/templates/
CMD ["python", "server.py"]
