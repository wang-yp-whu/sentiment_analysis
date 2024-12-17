# 舆情分析系统-布置在网页上
## 1.系统的启动
运行app.py 在浏览器中输入https://127.0.0.1:5000
之后就可以打开页面，跟随页面上的按钮可以完成验收时的可视化操作
## 2.各个文件夹的作用
-.venv 环境配置

-static 各个脚本运行时生成的文件

-templates 前端html源码

-utils python源码

-app.py 整个实验的启动

-stop_words.txt 停用词表，用于筛选话题

-simhei 设置中文字体，用于词云的生成

## 3.注意事项
启动app.py之前，按照get_random_data.py（爬取非热搜数据，爬取页数建议重点部分5页，非重点2页，参见代码line79-82）->
->statics.py（数据统计，生成词云）->topic_analysis.py（话题分析）->sentiment.py
->sentiment_analysis_plus（情感分析进阶-细粒度）.py的顺序运行一遍（注意更换cookie.py中的cookie为你的最新cookie）

##4.新增日期和数据管理功能
如3注意事项依次运行修改后的程序，static中将自动根据当前的日期 保留当前的分析数据
（测试的话可以跑一遍然后改下文件夹名字再跑，又有新的数据了）
app运行后新增的修改后的网页新增下拉框展示了已有的分析数据，可以进行选择 日期/文件名