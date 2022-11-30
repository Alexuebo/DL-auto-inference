# DL-auto-inference
基于深度学习自动分割的推理软件
--

#### 使用方法：

1.安装必要的库 pip install -r requirements.txt

注意，pytorch直接下可能和版本不匹配，在[这里看版本](https://download.pytorch.org/whl/torch_stable.html)

我下载的是[torch1.12.1+cu116+py37](https://download.pytorch.org/whl/cu116/torch-1.12.1%2Bcu116-cp37-cp37m-win_amd64.whl
)

2.运行appMain.py

#### 目前已集成训练模型：
+ CT气胸 
    + 使用 Attention U-Net+肺野分割提取模型
    + 运行截图：
    + ![CT气胸推理](/resouces/pics/气胸推理.jpg)
+ CT肾肿瘤
    + 使用混合监督的nnu-net模型
    + 运行截图
    + ![CT肾肿瘤推理](/resouces/pics/肾肿瘤.png)
   

基于PyQt5开发；pytorch+cu116推理

版本v0.2