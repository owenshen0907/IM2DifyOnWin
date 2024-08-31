# 简介

> **本项目是在Tishon1532/chatgpt-on-wechat-win基础上，在中国最多人使用的IM上接入大模型能力**
> **IM接入使用的是chatgpt-on-wechat项目的能力，具体实现方式在这里就不赘述了，请移步前述项目寻求答案**
> **LLM的工作流使用的Dify，基于此会实现，RAG，图片分析，web_search,文本生成图片，通讯内容总结，以及广告，投预警等功能**
> **本项目仅供学习和技术研究，请勿用于非法用途，如有任何人凭此做何非法事情，均于作者无关，特此声明。**
> **只能在Win平台运行项目！只能在Win平台运行项目！只能在Win平台运行项目!  （ 重要的事情说三遍 ）**


# 快速开始

## 准备

### 1.运行环境

仅支持Windows 系统同时需安装 `Python`。
> 建议Python版本使用 3.9.18 之间。

**(1) 下载项目代码：**

**(2) 安装核心依赖 (必选)：**
pip3 install -r requirements.txt

## 配置
配置文件的模板在根目录的`config-template.json`中，需复制该模板创建最终生效的 `config.json` 文件：
  cp config-template.json config.json
