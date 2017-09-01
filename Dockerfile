# Set the base image to the base image
FROM python:3.6

# ----
# Put your app-specific stuff here (extra yum installs etc).
# Any unique environment variables your config.py needs should also be added as ENV entries here

EXPOSE 8080

ENV PYTHONUNBUFFERED=yes \
    LOG_LEVEL=DEBUG \
    APP_NAME=property-api \
    MAX_HEALTH_CASCADE=6 \
    PORT=8080 \
    COMMIT=LOCAL \
    PYTHONPATH=/src \
    SENDFILE=0 \
    TEMPLATES_AUTO_RELOAD=true

WORKDIR /src

RUN pip install gunicorn eventlet

CMD ["/usr/local/bin/gunicorn", "-k", "eventlet", "--pythonpath", "/src", "--access-logfile", "-", "manage:manager.app", "--reload"]

# ----

# Get the python environment ready.
# Have this at the end so if the files change, all the other steps don't need to be rerun. Same reason why _test is
# first. This ensures the container always has just what is in the requirements files as it will rerun this in a
# clean image.
ADD requirements_test.txt requirements_test.txt
ADD requirements.txt requirements.txt
RUN pip3 install -q -r requirements.txt && \
  pip3 install -q -r requirements_test.txt
