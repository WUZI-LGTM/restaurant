# -*- coding: utf-8 -*-
"""
客家菜馆 · 扫码点餐系统（一键部署版）
前台：/        顾客点餐
后台：/admin   订单管理 + 菜品管理
数据库：SQLite（内置，无需单独配置）
"""
import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template, g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "restaurant.db")

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


# ---------- 数据库 ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


DEFAULT_DISHES = [
    ("🥣 汤类","赤豆龙骨鸡汤",58,"小份58/大份68"),("🥣 汤类","黑蒜龙骨鸡汤",58,"小份58/大份68"),
    ("🥣 汤类","鹿茸菌龙骨汤",58,"小份58/大份68"),("🥣 汤类","牛大力龙骨鸡汤",68,"小份68/大份78"),
    ("🥣 汤类","五指毛桃鸡汤",68,"小份68/大份78"),("🥣 汤类","回春草鸡汤",68,"小份68/大份78"),
    ("🥣 汤类","金线莲鸡汤",68,"小份68/大份78"),("🥣 汤类","生地土伏汤",68,"小份68/大份78"),
    ("🥣 汤类","花旗参炖鸡汤",78,"小份78/大份88"),("🥣 汤类","羊肚菌炖鸡汤",78,"小份78/大份88"),
    ("🥣 汤类","桑黄石斛鸡汤",78,"小份78/大份88"),("🥣 汤类","石斛鸡汤",78,"小份78/大份88"),
    ("🥣 汤类","新会陈皮鸡汤",78,"小份78/大份88"),("🥣 汤类","黑松露鸡汤",88,"小份88/大份98"),
    ("🥣 汤类","虫草养生汤",0,"时价"),
    ("⭐ 店长推荐","羊胎盘药膳鸡煲",198,"小份198/大份268"),("⭐ 店长推荐","白切农家土鸡",158,""),
    ("⭐ 店长推荐","荷叶蒸土鸡",158,""),("⭐ 店长推荐","五指毛桃焗鸡",158,""),
    ("⭐ 店长推荐","特色果园盐水鸡",138,""),("⭐ 店长推荐","古法焖羊肉",138,""),
    ("⭐ 店长推荐","油焖罗氏虾",138,""),("⭐ 店长推荐","避风塘爆梭子蟹",118,""),
    ("⭐ 店长推荐","碌鹅",108,""),("⭐ 店长推荐","古法焖山猪肉",98,""),
    ("⭐ 店长推荐","沙葱炒黄鳝",98,""),("⭐ 店长推荐","卤鹅",98,""),("⭐ 店长推荐","烧鹅",98,""),
    ("⭐ 店长推荐","老酒猪脚焖鸡爪",88,""),("⭐ 店长推荐","红腰豆焗牛尾",88,""),
    ("⭐ 店长推荐","特色辣子鸡",88,""),("⭐ 店长推荐","避风塘爆大虾",88,""),
    ("⭐ 店长推荐","沙姜牛蹄",78,""),("⭐ 店长推荐","笋尖炒牛肉",78,""),
    ("⭐ 店长推荐","野生菌炒山猪肉",78,""),("⭐ 店长推荐","小黄瓜炒牛肉",78,""),
    ("⭐ 店长推荐","头道竹牛肉煲",78,""),("⭐ 店长推荐","鲍汁凤爪煲",68,""),
    ("⭐ 店长推荐","野生菌牛肉炒饭",58,""),("⭐ 店长推荐","新鲜核桃百合",58,""),
    ("⭐ 店长推荐","松子玉米青豆",48,""),("⭐ 店长推荐","笋尖炒五花肉",48,""),
    ("⭐ 店长推荐","招牌焗南瓜",38,""),("⭐ 店长推荐","蒸菩米米粉",38,""),
    ("⭐ 店长推荐","秘制豆腐",38,""),
    ("🍲 客家菜","脆皮吊烧鸡",158,""),("🍲 客家菜","糟花牛百叶",88,""),
    ("🍲 客家菜","脆皮乳鸽",88,""),("🍲 客家菜","墨鱼干蒸猪脚",78,""),
    ("🍲 客家菜","沙姜炒猪利",78,""),("🍲 客家菜","黑椒铁板牛仔骨",78,""),
    ("🍲 客家菜","鹿茸菌炒牛肉",78,""),("🍲 客家菜","水煮牛肉",78,""),
    ("🍲 客家菜","椒盐猪脚",68,""),("🍲 客家菜","凉拌牛肉",68,""),
    ("🍲 客家菜","滑哥酿豆腐",68,""),("🍲 客家菜","鼓汁蒸排骨",68,""),
    ("🍲 客家菜","爆炒腰花",68,""),("🍲 客家菜","蒜香骨",68,""),
    ("🍲 客家菜","椒盐扇骨",68,""),("🍲 客家菜","酸甜排骨",68,""),
    ("🍲 客家菜","红烧猪肉",68,""),("🍲 客家菜","椒盐排骨",68,""),
    ("🍲 客家菜","沙葱炒猪利",58,""),("🍲 客家菜","炒猪肠",58,""),
    ("🍲 客家菜","椒盐粉肠",58,""),("🍲 客家菜","马鲛鱼干蒸五花肉",58,""),
    ("🍲 客家菜","藕尖炒猪肠",58,""),("🍲 客家菜","咸菜炒猪肠",58,""),
    ("🍲 客家菜","麻婆豆腐",48,""),("🍲 客家菜","香芋蒸五花肉",48,""),
    ("🍲 客家菜","榄角蒸五花肉",48,""),
    ("🫕 煲仔菜","生焗粉肠",58,""),("🫕 煲仔菜","酿三宝",58,""),
    ("🫕 煲仔菜","红腰豆焗猪尾",58,""),("🫕 煲仔菜","香芋芡实煲",48,""),
    ("🫕 煲仔菜","酿茄子",48,""),("🫕 煲仔菜","菜脯炒猪耳",48,""),
    ("🫕 煲仔菜","杂菌煲",48,""),("🫕 煲仔菜","香菇酿豆腐",38,""),
    ("🫕 煲仔菜","咸菜猪红煲",38,""),("🫕 煲仔菜","咸菜粉丝煲",38,""),
    ("🫕 煲仔菜","酿辣椒",38,""),("🫕 煲仔菜","酿苦瓜",38,""),
    ("🫕 煲仔菜","酿鸡蛋",38,""),
    ("🦞 海鲜","清蒸小青龙",0,"时价"),("🦞 海鲜","蒜蓉蒸生蚝",0,"时价"),
    ("🦞 海鲜","蒜蓉粉丝蒸带子",138,""),("🦞 海鲜","鲍汁扣鲜鲍",138,""),
    ("🦞 海鲜","豆鼓蒸白鳝",138,""),("🦞 海鲜","串烧白鳝",138,""),
    ("🦞 海鲜","清蒸老虎斑",118,""),("🦞 海鲜","盐焗花螺",118,""),
    ("🦞 海鲜","避风塘爆梭子蟹",118,""),("🦞 海鲜","蒜蓉开边虾",98,""),
    ("🦞 海鲜","椒盐大虾",98,""),("🦞 海鲜","清蒸多宝鱼",98,""),
    ("🦞 海鲜","避风塘爆大虾",88,""),("🦞 海鲜","盐焗海虾",88,""),
    ("🦞 海鲜","香煎黄花鱼",78,""),("🦞 海鲜","铁板鲜鱿",78,""),
    ("🦞 海鲜","清蒸鲈鱼",68,""),("🦞 海鲜","香煎金鲳鱼",68,""),
    ("🦞 海鲜","白灼鱿鱼仔",68,""),
    ("🥬 素菜","清炒叶菜",20,""),("🥬 素菜","青菜瓜菜",28,""),
    ("🥬 素菜","凉拌青瓜",30,""),("🥬 素菜","上汤时蔬",30,""),
    ("🥬 素菜","凉拌黑木耳",30,""),("🥬 素菜","炒芋荷",38,""),
    ("🐟 河鲜","清蒸翘嘴鱼",0,"时价"),("🐟 河鲜","清蒸青竹鱼",0,"时价"),
    ("🐟 河鲜","野生甲鱼蒸土鸡",0,"时价"),("🐟 河鲜","野生甲鱼焖鸡",0,"时价"),
    ("🐟 河鲜","豆鼓蒸鲟龙鱼",168,""),("🐟 河鲜","盐焗罗氏虾",138,""),
    ("🐟 河鲜","榄角蒸石坚鱼",118,""),("🐟 河鲜","砂锅焗黄角鱼",98,""),
    ("🐟 河鲜","沙葱炒黄鳝",98,""),("🐟 河鲜","黄角鱼菜脯煲",98,""),
    ("🐟 河鲜","砂锅焗清江鱼",88,""),("🐟 河鲜","酸菜鱼",68,""),
    ("🐟 河鲜","椒盐小河鱼",68,""),("🐟 河鲜","河鱼河虾双拼",68,""),
    ("🐟 河鲜","生焗雄头",68,""),("🐟 河鲜","剁椒鱼头",68,""),
    ("🍣 鱼生","草鱼鱼生",80,"须提前预定"),("🍣 鱼生","鲫鱼鱼生",90,"须提前预定"),
    ("🍣 鱼生","赤眼鱼生",100,"须提前预定"),("🍣 鱼生","石坚鱼生",138,"须提前预定"),
    ("🍣 鱼生","青竹鱼生",168,"须提前预定"),("🍣 鱼生","虾生",128,"须提前预定"),
    ("🍚 主食","榨菜",3,"小碟"),("🍚 主食","花生米",5,"小碟"),
    ("🍚 主食","榄角",5,"小碟"),("🍚 主食","饭",10,"份"),
    ("🍚 主食","菩米粥",15,""),("🍚 主食","马鲛鱼",15,"小碟"),
    ("🍚 主食","馒头",18,"打"),("🍚 主食","金银馒头",28,"打"),
    ("🍚 主食","核桃包",28,"打"),("🍚 主食","炒米粉",28,""),
    ("🍚 主食","炒面",28,""),
    ("🥤 饮料","平安泉弱碱活泉水350ml",3,""),("🥤 饮料","进口无酒精红酒750ml",98,""),
    ("🥤 饮料","卡士奶428ml",25,""),("🥤 饮料","椰子汁1250ml",25,""),
    ("🥤 饮料","苹果醋330ml",5,""),("🥤 饮料","百事330ml",5,""),
    ("🥤 饮料","菠萝啤330ml",5,""),("🥤 饮料","加多宝310ml",5,""),
    ("🥤 饮料","五年陈皮黄芪水500ml",5,""),("🥤 饮料","黄精佛手草本500ml",5,""),
    ("🥤 饮料","雪碧330ml",5,""),("🥤 饮料","雪碧2L",10,""),
    ("🥤 饮料","果粒橙1.25L",15,""),("🥤 饮料","百事2L",10,""),
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT NOT NULL UNIQUE,
            table_no TEXT NOT NULL,
            people_num TEXT,
            remark TEXT,
            goods TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT '待处理',
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL DEFAULT 0,
            spec TEXT DEFAULT '',
            sort INTEGER DEFAULT 0
        )
    """)
    cnt = conn.execute("SELECT COUNT(*) FROM dishes").fetchone()[0]
    if cnt == 0:
        for i, (cat, name, price, spec) in enumerate(DEFAULT_DISHES):
            conn.execute("INSERT INTO dishes (category,name,price,spec,sort) VALUES (?,?,?,?,?)",
                         (cat, name, price, spec, i))
        conn.commit()
    conn.close()


# ---------- 页面 ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")


# ---------- 菜品 API ----------
@app.route("/api/dishes")
def list_dishes():
    db = get_db()
    rows = db.execute("SELECT * FROM dishes ORDER BY sort ASC").fetchall()
    cats = {}
    for r in rows:
        d = dict(r)
        cats.setdefault(d["category"], []).append(d)
    return jsonify({"ok": True, "data": [{"category": c, "items": v} for c, v in cats.items()]})


@app.route("/api/dish", methods=["POST"])
def add_dish():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    category = (data.get("category") or "").strip()
    if not name or not category:
        return jsonify({"ok": False, "msg": "菜品名和分类不能为空"}), 400
    price = float(data.get("price") or 0)
    spec = (data.get("spec") or "").strip()
    db = get_db()
    mx = db.execute("SELECT COALESCE(MAX(sort),0) FROM dishes").fetchone()[0]
    cur = db.execute("INSERT INTO dishes (category,name,price,spec,sort) VALUES (?,?,?,?,?)",
                     (category, name, price, spec, mx + 1))
    db.commit()
    return jsonify({"ok": True, "id": cur.lastrowid})


@app.route("/api/dish/<int:did>", methods=["PUT"])
def update_dish(did):
    data = request.get_json(force=True)
    db = get_db()
    fields, vals = [], []
    for k in ("category", "name", "spec"):
        if k in data:
            fields.append(f"{k}=?")
            vals.append(str(data[k]).strip())
    if "price" in data:
        fields.append("price=?")
        vals.append(float(data["price"]))
    if not fields:
        return jsonify({"ok": False, "msg": "没有要更新的字段"}), 400
    vals.append(did)
    cur = db.execute(f"UPDATE dishes SET {','.join(fields)} WHERE id=?", vals)
    db.commit()
    if cur.rowcount == 0:
        return jsonify({"ok": False, "msg": "菜品不存在"}), 404
    return jsonify({"ok": True})


@app.route("/api/dish/<int:did>", methods=["DELETE"])
def delete_dish(did):
    db = get_db()
    db.execute("DELETE FROM dishes WHERE id=?", (did,))
    db.commit()
    return jsonify({"ok": True})


@app.route("/api/dishes/reset", methods=["POST"])
def reset_dishes():
    db = get_db()
    db.execute("DELETE FROM dishes")
    for i, (cat, name, price, spec) in enumerate(DEFAULT_DISHES):
        db.execute("INSERT INTO dishes (category,name,price,spec,sort) VALUES (?,?,?,?,?)",
                   (cat, name, price, spec, i))
    db.commit()
    return jsonify({"ok": True, "count": len(DEFAULT_DISHES)})


# ---------- 订单 API ----------
@app.route("/api/order", methods=["POST"])
def create_order():
    data = request.get_json(force=True)
    table_no = (data.get("tableNo") or "").strip()
    if not table_no:
        return jsonify({"ok": False, "msg": "请填写桌号"}), 400
    goods = data.get("goods") or []
    if not goods:
        return jsonify({"ok": False, "msg": "购物车为空"}), 400
    total = float(data.get("total") or 0)
    order_no = "D" + datetime.now().strftime("%Y%m%d%H%M%S") + str(os.getpid())[-3:]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db = get_db()
    db.execute("INSERT INTO orders (order_no,table_no,people_num,remark,goods,total,created_at) VALUES (?,?,?,?,?,?,?)",
               (order_no, table_no, data.get("peopleNum") or "", data.get("remark") or "",
                json.dumps(goods, ensure_ascii=False), total, created_at))
    db.commit()
    return jsonify({"ok": True, "orderNo": order_no, "createdAt": created_at})


@app.route("/api/orders")
def list_orders():
    status = request.args.get("status", "")
    db = get_db()
    if status:
        rows = db.execute("SELECT * FROM orders WHERE status=? ORDER BY id DESC", (status,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["goods"] = json.loads(d["goods"])
        result.append(d)
    return jsonify({"ok": True, "data": result})


@app.route("/api/order/<int:oid>/status", methods=["POST"])
def update_status(oid):
    data = request.get_json(force=True)
    status = (data.get("status") or "").strip()
    if status not in ("待处理", "制作中", "已完成", "已取消"):
        return jsonify({"ok": False, "msg": "状态不合法"}), 400
    db = get_db()
    cur = db.execute("UPDATE orders SET status=? WHERE id=?", (status, oid))
    db.commit()
    if cur.rowcount == 0:
        return jsonify({"ok": False, "msg": "订单不存在"}), 404
    return jsonify({"ok": True})


@app.route("/api/order/<int:oid>", methods=["DELETE"])
def delete_order(oid):
    db = get_db()
    db.execute("DELETE FROM orders WHERE id=?", (oid,))
    db.commit()
    return jsonify({"ok": True})


@app.route("/api/stats")
def stats():
    db = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    row = db.execute("SELECT COUNT(*) cnt, COALESCE(SUM(total),0) amt FROM orders WHERE created_at LIKE ?",
                     (today + "%",)).fetchone()
    pending = db.execute("SELECT COUNT(*) FROM orders WHERE status='待处理'").fetchone()[0]
    return jsonify({"ok": True, "todayCount": row["cnt"], "todayAmount": round(row["amt"], 2), "pending": pending})


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
