from flask import Flask, request, jsonify
import re
from run import app
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 初始化限流器
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["2 per minute"]
)

def show_link(link):
    ua_phone = 'Mozilla/5.0 (Linux; Android 6.0; ' \
             'Nexus 5 Build/MRA58N) AppleWebKit/537.36 (' \
             'KHTML, like Gecko) Chrome/80.0.3987.116 Mobile Safari/537.36'

    headers = {
            'User-Agent': ua_phone
        }
    try:
        res = requests.get(link,headers=headers).text
        pattern = r"https:\\u002F\\u002Faweme\.snssdk\.com\\u002Faweme\\u002Fv1\\u002Fplaywm\\u002F\?video_id=[a-zA-Z0-9]+&ratio=[0-9a-z]+&line=[0-9]+"
        match = re.search(pattern, res)

        # 如果找到匹配的URL，将\u002F替换为空字符"/"
        if match:
            url = match.group()
            # 替换\u002F为 /
            clean_url = re.sub(r"\\u002F", "/", url).replace("playwm","play")
            return clean_url
        else:
            return ""
    except:
        return ""

@app.errorhandler(429)
def handle_rate_limit_exceeded(e):
    return jsonify({"error": "请求频率超过限制",'code':400}), 200


def haldle_url(string):
    pattern = r'https://v.douyin.com/.*?/'
    match = re.search(pattern, string)
    if match:
        url = match.group()
        return url
    return 0

@app.route('/get_video_url', methods=['POST'])
@limiter.limit("2 per minute")  # 限流配置
def get_video_url():
    data = request.json
    shared_url = data.get("shared_url")
    handle_link = haldle_url(shared_url)
    if not handle_link:
        return jsonify({"error": "分享链接非法", 'code': 400}), 200
    link = show_link(handle_link.strip())
    return jsonify({"video_url": link})
