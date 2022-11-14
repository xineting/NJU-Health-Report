# 一、更新时间
2022年5月21日，获得核酸打卡列表的函数GetList，需要使用cookie才能访问了，更新了GetCookie函数和GetList函数
2022年11月15日，现在大卡需要手机验证码，大概5-7天要验证一次。

# 二、使用库
- selemium
- easyocr
- request

# 三、功能
1、核算上报时间为每过2天自动+2

2、填报的地址为你昨天填报的地址复制过来的。
3、自动登陆，可以过验证码


# 四、用户自己需要完成的：
## 1、登陆账号密码修改

修改main函数中21 22行

```python
username = '111111'  # 用户名
password = '11111
```
## 2、手机验证码

随便在一个pc端访问
http://authserver.nju.edu.cn/authserver/index.do

将我们的账号密码输入，如果登陆成功需要验证码的时候，我们进行手机验证码验证。

之后使用python main.py脚本运行我们的程序，看是否打卡成功。

## 3、ubuntu自己挂个定时任务cron
百度一下
