FROM library/python:3.7.5-slim

# install python
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# copy application and set work directory
WORKDIR /app
COPY . /app

# expose ports and set command
EXPOSE 80
CMD python scrum_master_jr.py
