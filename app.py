import os
from flask import (
    Flask,
    request,
    url_for,
    current_app,
    abort,
    make_response,
)
from werkzeug.utils import secure_filename
from flask import send_from_directory
import random, time
import getConfig as gcf

cf = gcf.get_config()

allowed_extensions = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}
upload_folder = os.path.join(os.getcwd(), "pics")
print(upload_folder)
app = Flask(__name__, instance_relative_config=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


# https://www.cnblogs.com/huchong/p/8951715.html
def create_date_folder(filename):
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print("localtime=" + localtime)
    year = time.strftime("%Y", time.localtime(time.time()))
    month = time.strftime("%m", time.localtime(time.time()))
    day = time.strftime("%d", time.localtime(time.time()))
    fileYear = upload_folder + "/" + year
    fileMonth = fileYear + "/" + month
    fileDay = fileMonth + "/" + day

    if not os.path.exists(fileYear):
        os.mkdir(fileYear)
        os.mkdir(fileMonth)
        os.mkdir(fileDay)
    else:
        if not os.path.exists(fileMonth):
            os.mkdir(fileMonth)
            os.mkdir(fileDay)
        else:
            if not os.path.exists(fileDay):
                os.mkdir(fileDay)

    print(year + "/" + month + "/" + day + "/" + filename)
    return year + "/" + month + "/" + day + "/" + filename


@app.route("/", methods=["POST"])
def upload_file():
    if request.method == "POST":
        # 检查post请求中是否有文件
        if "file" not in request.files:
            print("你没有上传文件！")
            abort(400)
        file = request.files["file"]
        print(file)
        if file.filename == "":
            print("你没有选择文件！")
            abort(400)
        if file and allowed_file(file.filename):
            try:
                filepath = create_date_folder(file.filename)
                file.save(os.path.join(upload_folder, filepath))
                if app.config["running_port"] != 80:
                    img_url = ("http://" + app.config["running_domain"] + ":" + str(app.config["running_port"]) + url_for("uploaded_file", filepath=filepath))
                else:
                    img_url = ("http://" + app.config["running_domain"] + url_for("uploaded_file", filepath=filepath))
                response = make_response(img_url, 200)
                response.mimetype = "text/plain"
                return response
            except Exception as e:
                print("出现错误！")
                print(e.args)
                abort(400)
        else:
            print("不被服务器支持的文件！")
            abort(400)


@app.route("/uploads/<path:filepath>")
def uploaded_file(filepath):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filepath)



if __name__ == "__main__":
    app.config["UPLOAD_FOLDER"] = upload_folder
    app.config["running_domain"] = cf["running_domain"]
    app.config["running_port"] = cf["port"]
    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * int(cf["max_length"])
    app.config.from_mapping(
        SECRET_KEY="dgvbv43@$ewedc",
        DATABASE=os.path.join(app.instance_path, "my-easy-pic-bed.sqlite"),
    )
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    try:
        os.mkdir(upload_folder)
    except Exception as e:
        pass

    app.run(
        debug=False, host=app.config["running_domain"], port=app.config["running_port"]
    )
