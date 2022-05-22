import string
import uuid
import random
import time
import MySQLdb
from flask import Flask, request, jsonify, abort
import re

app = Flask(__name__)

# 短信超时时间 15 分钟
SMS_EXPIRE_TIME = 15 * 60


def random_string():
    return str(uuid.uuid4().hex)


def random_code(length=6):
    return ''.join(random.sample(string.digits, length))


class MysqlUtils(object):

    def __init__(self, db="test001", host="localhost", user="root", password=""):
        self.db = MySQLdb.connect(host, user, password, db, charset='utf8')
        self.cursor = self.db.cursor()

    def query_user(self, phone):
        self.cursor.execute(f"select * from user where phone='{phone}'")
        results = self.cursor.fetchall()
        if results:
            return results
        else:
            return None

    def query_sms(self, phone, code):
        n = int(time.time())
        self.cursor.execute(f"select * from sms where phone='{phone}' and code='{code}' and exprie_time>{n} and used=0")
        results = self.cursor.fetchall()
        if results:
            return results
        else:
            return None

    def insert_user(self, phone, pwd):

        sql = f"INSERT INTO user(phone, password) VALUES ('{phone}', '{pwd}')"
        self.cursor.execute(sql)
        self.db.commit()

    def insert_user_token(self, user_id, token):
        sql = f"INSERT INTO token(user_id, token) VALUES ({user_id}, '{token}')"
        self.cursor.execute(sql)
        self.db.commit()

    def query_token(self, token):
        sql = f"select * from token where token='{token}'"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results

    def insert_sms(self, phone):
        code = random_code(6)
        create_time = int(time.time())
        expire_time = create_time + SMS_EXPIRE_TIME
        sql = f"INSERT INTO sms(phone, code, used, exprie_time, created_time) VALUES ('{phone}', '{code}', 0, '{expire_time}', '{create_time}')"
        self.cursor.execute(sql)
        self.db.commit()

    def set_sms_used(self, phone, code):
        sql = f"UPDATE sms set used=1 where phone='{phone}' and code='{code}'"
        self.cursor.execute(sql)
        self.db.commit()


def query_user(phone):
    pass


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/callback", methods=["POST"])
def callback():
    data = request.json
    print(data, "callback")
    return "<p>Hello, World!</p>"


@app.route("/register", methods=['POST'])
def register():
    """
        注册
    :return:
    """
    data = request.json
    # 1： 账号密码  2： 验证码
    register_type = data.get("type", 1)
    phone = data.get("phone")
    if not phone:
        abort(400, '手机号不能为空')
    reg = "1[3|4|5|7|8][0-9]{9}"
    m = re.findall(reg, phone)
    if not m:
        abort(400, "电话号码非法")
    password = data.get("password")
    if not password:
        abort(400, '密码不能为空')
    if register_type == 1:
        db_utils = MysqlUtils()
        res = db_utils.query_user(phone=phone)
        if not res:
            db_utils.insert_user(phone=phone, pwd=password)
            return jsonify({"phone": "phone"})
        else:
            abort(400, '用户名已经存在')
    else:
        phone = data.get("phone")
        code = data.get("code")
        if not code:
            abort(400, '验证码不能为空')
        db_utils = MysqlUtils()
        res = db_utils.query_sms(phone=phone, code=code)
        if not res:
            abort(400, "验证码不正确或超时")
        else:
            res = db_utils.query_user(phone=phone)
            if not res:
                db_utils.insert_user(phone=phone, pwd=password)
                db_utils.set_sms_used(phone=phone, code=code)
                return jsonify({"phone": phone})
            else:
                abort(400, '用户名已经存在')


@app.route("/login", methods=['POST'])
def login():
    """
        登录
    :return:
    """
    data = request.json
    phone = data.get("phone")
    password = data.get("password")
    if not phone or not password:
        abort(400, '账号密码不能为空')
    db_utils = MysqlUtils()
    res = db_utils.query_user(phone=phone)
    if not res:
        return jsonify({"message": "用户不存在"})
    else:
        user = res[0]
        token = random_string()
        db_utils.insert_user_token(user_id=user[0], token=token)
        return jsonify({
            "id": user[0],
            "phone": user[1],
            "token": token
        })


@app.route("/sms", methods=['POST'])
def sms():
    data = request.json
    phone = data.get("phone")
    if not phone:
        abort(400, "电话号码是必须的")
    reg = "1[3|4|5|7|8][0-9]{9}"
    m = re.findall(reg, phone)
    if not m:
        abort(400, "电话号码非法")
    db_utils = MysqlUtils()
    db_utils.insert_sms(phone=phone)
    return jsonify({"status": "success"})


@app.route("/questions", methods=['GET'])
def questions():
    db_utils = MysqlUtils()
    token = request.args.get('token')
    if not token:
        abort(400, "请登录")
    res = db_utils.query_token(token)
    return jsonify({
        "items": [
            {
                "title": "你问的题目1"
            },
            {
                "title": "你问的题目2"
            }
        ]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)