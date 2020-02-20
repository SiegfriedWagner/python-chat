cd "$(dirname "$0")" || exit
echo "$PWD"
python -m venv ./venv-linux
source ./venv-linux/bin/activate
python -m pip install -r ./requirements.txt