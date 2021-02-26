sudo systemctl start redis
python3 /LMSApp/manage.py makemigrations
python3 /LMSApp/manage.py migrate
