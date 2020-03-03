cd "$(dirname "$0")" || exit
echo "$PWD"
python -m venv ./venv-linux
source ./venv-linux/bin/activate
python -m pip install -r ./requirements.txt

echo 'cd "$(dirname "$0")" || exit
./venv-linux/bin/python -m chat.client.client_setup' > run_client.sh
echo 'cd "$(dirname "$0")" || exit
./venv-linux/bin/python -m chat.server.qt_server' > run_server.sh