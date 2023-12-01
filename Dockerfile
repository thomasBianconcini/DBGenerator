FROM python:3.8-slim

WORKDIR /app

#Copying your application files to the container
COPY . /app

#Installing required Python packages
RUN pip install --no-cache-dir Faker Flask pandas sqlite_web  

EXPOSE 5000
#Installing SQLite3 for database interaction
#RUN my_db.py
#Command to run your Flask app

CMD ["sqlite_web","-H", "0.0.0.0", "-p", "5000", "people.db"]