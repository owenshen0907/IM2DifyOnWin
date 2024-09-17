# 简介

> **本项目是在Tishon1532/chatgpt-on-wechat-win基础上，在国内最多人使用的IM上接入大模型能力**
> **IM接入使用的是chatgpt-on-wechat项目的能力，具体实现方式在这里就不赘述了，请移步前述项目寻求答案**
> **LLM的工作流使用的Dify，基于此会实现，RAG，图片分析，web_search,文本生成图片，通讯内容总结，以及广告，投预警等功能**
> **本项目仅供学习和技术研究，请勿用于非法用途，如有任何人凭此做何非法事情，均于作者无关，特此声明。**
> **本项目仅能在Win平台运行！**

# 项目目录结构
>**bot|对话机器人接口**  
>**bridge|用于桥接不同bot**  
>**channel｜监听IM消息，并做处理**  
>**common｜**  
>**plugins｜**  
>**venv｜**  
>**voice｜**  
>**app.py｜启动程序**  
>**config.json｜配置文件**  
>**config.py｜配置文件说明**  
>**requirements.txt｜必要依赖**  
>**requirements-optional.txt｜可选依赖**  

# 快速开始

## 准备

### 1.运行环境
仅支持Windows 系统同时需安装 `Python`。
> 建议Python版本使用 3.9.18版本。  
> 如果本地环境一直调试不好可以使用我这边的conda环境，为了更好的迁移，建议各位开发者也适用conda.  
**conda迁移**具体操作可以看我后面贴的过程。如果你们想直接用我的conda环境，也可直接联系我GitHub上没法上传大文件   
>(stepFun-on-wechat) PS D:\PycharmProjects\chatgpt-on-wechat-win> conda info --envs   
># conda environments:  
>#   
>base                     C:\Users\EDY\miniconda3  
>stepFun-on-wechat     *  C:\Users\EDY\miniconda3\envs\stepFun-on-wechat  
>(stepFun-on-wechat) PS D:\PycharmProjects\chatgpt-on-wechat-win> conda install conda-pack  
>Solving environment: done   
>## Package Plan ##  
>  environment location: C:\Users\EDY\miniconda3\envs\stepFun-on-wechat  
>  added / updated specs:  
>    - conda-pack  
>The following packages will be downloaded:  
>    package                    |            build   
>    ---------------------------|-----------------  
>    conda-pack-0.7.1           |   py38haa95532_0          73 KB  
>    ------------------------------------------------------------
>                                           Total:          73 KB  
>The following NEW packages will be INSTALLED:   
>   
>  conda-pack         pkgs/main/win-64::conda-pack-0.7.1-py38haa95532_0   
>Proceed ([y]/n)? y   
>Downloading and Extracting Packages:                                                                                                  
>Preparing transaction: done  
>Verifying transaction: done  
>Executing transaction: done  
>(stepFun-on-wechat) PS D:\PycharmProjects\chatgpt-on-wechat-win> conda pack -n stepFun-on-wechat  
>Collecting packages...   
>Packing environment at 'C:\\Users\\EDY\\miniconda3\\envs\\stepFun-on-wechat' to 'stepFun-on-wechat.tar.gz'   
>[########################################] | 100% Completed | 37.1s   
>(stepFun-on-wechat) PS D:\PycharmProjects\chatgpt-on-wechat-win> conda pack -n stepFun-on-wechat -o D:/stepFun-on-wechat.tar.gz  
>Collecting packages...   
>Packing environment at 'C:\\Users\\EDY\\miniconda3\\envs\\stepFun-on-wechat' to 'D:/stepFun-on-wechat.tar.gz'  
>[########################################] | 100% Completed | 19.2s    
**截止到此在原电脑上的conda环境就备份好了，文件是D:/stepFun-on-wechat.tar.gz。下面是在新电脑上把在老电脑上备份的文件，解压到conda的evns目录下。后面的命令是激活conda环境。  
> (base) PS C:\Users\Administrator> conda info --envs  
># conda environments:  
>base                  *  C:\ProgramData\miniconda3  
>(base) PS C:\Users\Administrator> conda activate stepFun-on-wechat  
### 2.下载项目代码   
下载后面链接代码到本地即可：https://github.com/owenshen0907/IM2DifyOnWin.git
### 3.选用第一步激活的conda环境  
>也可以不用我的conda环境，自己解决依赖问题即可
>pip3 install -r requirements.txt

### 4.配置
配置文件的模板在根目录的`config-template.json`中，需复制该模板创建最终生效的 `config.json` 文件：
  cp config-template.json config.json
### 5.运行
配置好相关信息后即可运行

### 6.QA
可以直接填issue或者邮件我owenshen123@outlook.com

