# 简介

> **本项目是在Tishon1532/chatgpt-on-wechat-win基础上，在国内最多人使用的IM上接入大模型能力**
> **IM接入使用的是chatgpt-on-wechat项目的能力，具体实现方式在这里就不赘述了，请移步前述项目寻求答案**
> **LLM的工作流使用的Dify，基于此会实现，RAG，图片分析，web_search,文本生成图片，通讯内容总结，以及广告，投预警等功能**
> **本项目仅供学习和技术研究，请勿用于非法用途，如有任何人凭此做何非法事情，均于作者无关，特此声明。**
> **本项目仅能在Win平台运行！**

# 项目目录结构
**bot|对话机器人接口**
**bridge|用于桥接不同bot**
**channel｜监听IM消息，并做处理**
**common｜**
**plugins｜**
**venv｜**
**voice｜**
**app.py｜启动程序**
**config.json｜配置文件**
**config.py｜配置文件说明**
**requirements.txt｜必要依赖**
**requirements-optional.txt｜可选依赖**

# 快速开始

## 准备

### 1.运行环境

仅支持Windows 系统同时需安装 `Python`。
> 建议Python版本使用 3.9.18版本。

**(1) 下载项目代码：**
下载后面链接代码到本地即可：https://github.com/owenshen0907/IM2DifyOnWin.git
**(2) 安装核心依赖 (必选)：**
pip3 install -r requirements.txt

## 配置
配置文件的模板在根目录的`config-template.json`中，需复制该模板创建最终生效的 `config.json` 文件：
  cp config-template.json config.json
## 运行
配置好相关信息后即可运行


相关问题可以加群进行交流
![image](https://github.com/user-attachments/assets/9505658c-5f92-413f-bdac-82331876528d)

