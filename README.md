# Cloudflare-Bulk-DNS
cloudflare批量添加dns解析 Cloudflare adds DNS resolution in batches

搭配https://www.itdog.cn/ping/ ping目标网站 以EdgeOne的优选ip为例

ping eo.hw.072103.xyz 或edgeone.ai 可以拿到优选ip 再配合该脚本使用

![undefined](https://m.360buyimg.com/i/jfs/t1/306417/34/19476/38866/6880587cF521bf4d1/3ef09137d9d7ef2f.png)

使用说明
---
提前准备好CloudFlare API和CloudFlare Zone ID
---
CloudFlare API创建方式和CloudFlare Zone ID
![undefined](https://m.360buyimg.com/i/jfs/t1/321521/11/18144/56036/688052a6F33fd312b/83829e1b3c366179.png)
![undefined](https://m.360buyimg.com/i/jfs/t1/306221/9/20310/21191/688052eeF9ce76cb0/d94213b7ed479a43.png)

运行时按脚本提示和个人需求输入
使用示例：
---
![undefined](https://m.360buyimg.com/i/jfs/t1/300476/31/24025/29537/688055deF5d3c8d86/1413e496b295e2b3.png)
---
可能遇到的错误信息
---
缺少 resources 依赖库

手动 运行 pip install requests 安装依赖即可

开始添加DNS记录...

⛔ [1/2] 请求失败 [@]: (HTTP 400) {"result":null,"success":false,"errors":[{"code":81058,"message":"An identical record already exists."}],"messages":[]}

⛔ [2/2] 请求失败 [@]: (HTTP 400) {"result":null,"success":false,"errors":[{"code":81058,"message":"An identical record already exists."}],"messages":[]}

此错误提示 在cloudflare dns解析中已有相同内容的解析 可以无视

第五步输入ip(优选ip时)切记要用“，”或空格隔开
