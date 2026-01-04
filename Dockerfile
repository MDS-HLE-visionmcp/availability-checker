# Use the official Apache Airflow image
FROM apache/airflow:2.8.1-python3.11

# Switch to root for system dependencies
USER root

# Install system dependencies for OpenCV (for RTSP stream checking)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy DAGs and supporting files
COPY --chown=airflow:root dags/ /opt/airflow/dags/
COPY --chown=airflow:root model.py /opt/airflow/dags/
COPY --chown=airflow:root config.py /opt/airflow/dags/

# Set environment variables
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__EXECUTOR=SequentialExecutor
ENV AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////opt/airflow/airflow.db
ENV AIRFLOW__WEBSERVER__SECRET_KEY=your-secret-key-change-in-production

# Copy entrypoint script
COPY --chown=airflow:root entrypoint.sh /opt/airflow/entrypoint.sh
RUN chmod +x /opt/airflow/entrypoint.sh

# Expose Airflow webserver port
EXPOSE 8080

# Override the default entrypoint and run our script
ENTRYPOINT []
CMD ["/bin/bash", "/opt/airflow/entrypoint.sh"]
