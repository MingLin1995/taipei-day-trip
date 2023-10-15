from flask import *  # pip install flask
from flask_cors import CORS  # 處理跨域問題 pip install flask-cors
# 導入 api/attractions.py 中的 attractions_bp
from api.attractions import attractions_bp
from api.mrts import mrts_bp
from api.user import user_bp
from api.booking import booking_bp
from api.order import order_bp


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # FLASK會將JSON資料的ASCII編碼
app.config["TEMPLATES_AUTO_RELOAD"] = True  # 修改templates會自動載入
# 設置應用程式的 SECRET_KEY（config屬性屬於Flask物件，不能設置到Blueprint）
app.config['SECRET_KEY'] = "密鑰可以是任何的字串，但是不要告訴別人"
CORS(app)  # 啟用CORS


# 註冊 Blueprint
app.register_blueprint(attractions_bp)
app.register_blueprint(mrts_bp)
app.register_blueprint(user_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(order_bp)


# Pages
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/attraction/<id>")
def attraction(id):
    return render_template("attraction.html")


@app.route("/booking")
def booking():
    return render_template("booking.html")


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
