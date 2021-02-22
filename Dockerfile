# start from an official image
FROM python:3.6

# arbitrary location choice: you can change the directory
# RUN mkdir -p ~/dockerLMS
WORKDIR /dockerLMS
# copy our project code
COPY . .
RUN ls -l 
RUN pip3 install -r requirements.txt
RUN pip3 install mysqlclient
# expose the port 8000
EXPOSE 8000

# define the default command to run when starting the container
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
