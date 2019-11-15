set ENV=%1

conda clean --lock

conda remove -n %ENV% --all

conda create --yes -n %ENV% python=2.7.8 scipy=0.18 numpy=1.11 matplotlib=1.5 pil=1.1.7 requests=2.4.1 more-itertools paramiko lxml

set OPENCV_DIR=D:\Autotests\setup\distr\opencv

set ENV_PACKAGES_DIR=C:\Anaconda2\envs\%ENV%\Lib\site-packages

copy %OPENCV_DIR%\cv2.pyd %ENV_PACKAGES_DIR%\cv2.pyd

activate %ENV% && pip install teamcity-messages==1.8 wand==0.4.1 ddt==1.2 dominate==2.3.5

activate %ENV% && pip install -U pure-python-adb

activate %ENV% && pip install Jinja2