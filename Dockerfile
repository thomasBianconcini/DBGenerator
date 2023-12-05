FROM python:3.8-slim

WORKDIR /app

#Copy your application files to the container
COPY . /app

#Installing required Python packages
RUN pip install --no-cache-dir sqlite_web

EXPOSE 5000

#Command to run your sqlite_web app
CMD ["sqlite_web","-H", "0.0.0.0", "-P", "-p", "5000", "fakeDB.db"]