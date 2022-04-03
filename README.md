
## Setup:
```
git submodule update --init --recursive
pip3 install -r ./requirements.txt
cd Parlai
pip3 install -r ./requirements.txt
python3 setup.py develop
```

## Run:
In one terminal:
```
python3 gui.py --alice
```
In another terminal (possibly another computer):
```
python3 gui.py --bob
```
*Alice must be started first!*
