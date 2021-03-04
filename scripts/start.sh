sudo systemctl start redis
source /root/envs.sh
python3 /LMSApp/manage.py makemigrations
python3 /LMSApp/manage.py migrate
