sudo rm -r /new_chatapp
pip3 install requirements.txt
fuser -k 8000/tcp
sudo systemctl stop redis