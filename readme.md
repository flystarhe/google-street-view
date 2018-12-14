# Google Street View

## test
```
python streetview.py
python streetview.py 30.657054,104.065665
```

## bash
```commandline
nohup python geo.py > logs.nohup.geo 2>&1 &
nohup python tool.py 100 > logs.nohup.tool 2>&1 &

nohup python main.py 10 images     > logs.nohup.main 2>&1 &
nohup python main.py 10 images 0   > logs.nohup.main 2>&1 &
nohup python main.py 10 images 90  > logs.nohup.main 2>&1 &
nohup python main.py 10 images 180 > logs.nohup.main 2>&1 &
nohup python main.py 10 images 270 > logs.nohup.main 2>&1 &
```
