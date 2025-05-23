import requests
import re
import subprocess
import time
import os
import urllib.parse as urlparse
import base64

def commit_and_push_to_github():
    # 从 Secrets 中获取访问令牌
    access_token = os.environ['urls']

    # 设置 Git 的身份验证信息
    os.system(f'git config --global user.email "you@example.com"')
    os.system(f'git config --global user.name "Your Name"')
    os.system(f'git config --global credential.helper store')

    # 添加更改、提交更改和推送更改
    os.system('git add cfip.txt')
    os.system(f'git commit -m "Update cfip.txt"')
    os.system(f'git push')


headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'priority': 'u=0, i',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'v2rayN/6.53',
}
params = {
    'token': 'auto',
}
proxies = {'all':os.environ['socksproxy']}  
urls = os.environ['urls']
mnurls = os.environ['mnurls']

# "hk", "香港", "hong kong", 
passnamelist = ["cmcc", "ct", "移动", "联通", "电信","unkown","香港","hk","hong kong","kr","jp","sg"]
urls = urls.split("\n")
mnurls = mnurls.split("\n")

urlipnum = 10
ipSet = []
extractedData = ""
start_time = time.time()

for urlraw in urls:
    nameCountMap = []
    # print(url)
    try:
        url = urlparse.urlparse(urlraw)
        if url.hostname == None:
            continue
        requesturl = url.scheme + "://" + url.hostname + url.path
        params = dict(urlparse.parse_qsl(url.query))
        response = requests.get(requesturl,  params=params, headers=headers)
        html_content = response.text
        # print(html_content)
        contents = base64.b64decode(html_content).decode('utf-8').split("\n")
        if len(contents) >30:
            urlipnum = 5
        else:
            urlipnum = 10
    except:
        print("Error url:" + urlparse.urlparse(urlraw).hostname)
        continue
    for content in contents:
        if not content.startswith(("vless", "trojan")):
            continue
        match = re.search(r'@((?:\d{1,3}\.){3}\d{1,3}):(\d+)', content)
        if match:
            hash_index = content.find('#')
            if hash_index != -1:
                name = content[hash_index + 1:]
            else:
                name = 'unknown'
            #统计名字出现的次数
            namecount = nameCountMap.count(name)
            if namecount >= 2:
                continue

            try:
                ip_address = match.group(1)
                # 去掉重复的IP地址
                if ip_address in ipSet:
                    continue
                port = int(match.group(2))
                cfip = "http://" + ip_address + ":" + str(port) + "/cdn-cgi/trace"
                cfipstatus = requests.get(cfip, timeout=1.5, verify=False, headers={'Connection': 'close'}, proxies=proxies)
            except:
                #print("Error content:" + content)
                continue
            if cfipstatus.status_code != 400:
                continue

            # 去掉特殊名字
            skip_content = False
            for item in passnamelist:
                if item in urlparse.unquote(name).lower():
                    skip_content = True
                    break
            if skip_content:
                continue

            if namecount == 0:
                newName = name
            else:
                newName = name + "~" + str(namecount)
            extractedData += content + "\n"
            ipSet.append(ip_address)
            nameCountMap.append(name)
            print("添加:" + newName + ", " + str(len(nameCountMap)))
            print('程序运行时间:%s秒' % ((time.time() - start_time)))
            #大于10个退出循环
            if len(nameCountMap) > urlipnum:
                break
    print('url运行时间:%s秒' % ((time.time() - start_time)))
    
for urlraw in mnurls:
    nameCountMap = []
    # print(url)
    try:
        url = urlparse.urlparse(urlraw)
        if url.hostname == None:
            continue
        requesturl = url.scheme + "://" + url.hostname + url.path
        params = dict(urlparse.parse_qsl(url.query))
        response = requests.get(requesturl,  params=params, headers=headers)
        html_content = response.text
        # print(html_content)
        contents = base64.b64decode(html_content).decode('utf-8').split("\n")
    except:
        print("Error mnurl:" + urlparse.urlparse(urlraw).hostname)
        continue
    for content in contents:
        if not content.startswith("vless"):
            continue
        match = re.search(r'@((?:\d{1,3}\.){3}\d{1,3}):(\d+)', content)
        if match:
            hash_index = content.find('#')
            if hash_index != -1:
                name = content[hash_index + 1:]
            else:
                name = 'unknown'
            #统计名字出现的次数
            namecount = nameCountMap.count(name)
            # if namecount >= 10:
            #     continue

            try:
                ip_address = match.group(1)
                # 去掉重复的IP地址
                if ip_address in ipSet:
                    continue
                port = int(match.group(2))
                cfip = "http://" + ip_address + ":" + str(port) + "/cdn-cgi/trace"
                cfipstatus = requests.get(cfip, timeout=1.5, verify=False, headers={'Connection': 'close'}, proxies=proxies)
            except:
                #print("Error content:" + content)
                continue
            if cfipstatus.status_code != 400:
                continue

            # 去掉特殊名字
            skip_content = False
            for item in passnamelist:
                if item in urlparse.unquote(name).lower():
                    skip_content = True
                    break
            if skip_content:
                continue

            if namecount == 0:
                newName = name
            else:
                newName = name + "~" + str(namecount)
            extractedData += content + "\n"
            ipSet.append(ip_address)
            nameCountMap.append(name)
            print("添加:" + newName + ", " + str(len(nameCountMap)))
            print('程序运行时间:%s秒' % ((time.time() - start_time)))
            #大于10个退出循环
            if len(nameCountMap) > 10:
                break
    print('mnurl运行时间:%s秒' % ((time.time() - start_time)))

with open('cfip.txt', 'w') as file2:
    cfipbase64 = base64.b64encode(extractedData.encode('utf-8')).decode("utf-8")
    file2.write(cfipbase64)
print("数据已经保存到 cfip.txt")
print('程序运行总时间:%s秒' % ((time.time() - start_time)))
commit_and_push_to_github()
