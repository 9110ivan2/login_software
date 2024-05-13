from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import psycopg2


app = Flask(__name__)
app.secret_key = "ivan9110"

login_manager = LoginManager()
login_manager.init_app(app)

conn = psycopg2.connect("dbname= login_info user=postgres password=postgres")

class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM login_table WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        if user_data:
            user = User()
            user.id = user_data[0]
            user.username = user_data[1]
            return user
        else:
            return None

@app.route("/")
def index():
    return redirect("register")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username","")
        password = request.form.get("password","")
        if username and password:
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO login_table (username, password) VALUES(%s, %s)",
                            (username, password)
                        )
            except psycopg2.errors.UniqueViolation:
                error_message = "Error! Try another username."
                return render_template("error.html", error_message=error_message)
            except psycopg2.errors.NotNullViolation:
                error_message = "Error! Add username or password."
                return render_template("error.html", error_message=error_message)
            except psycopg2.errors.CheckViolation:
                error_message = "Error! Password needs to be at least 8 symbols."
                return render_template("error.html", error_message=error_message)
            return redirect("success")
        else:
            error_message = "Error! Username or password cannot be empty"
            return render_template("error.html", error_message=error_message)
    return render_template("index.html")

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM login_table WHERE username = %s AND password= %s ",
                    (username, password)
                )
                account = cur.fetchone()
                if account:
                    user = User()
                    user.id = account[0]
                    return render_template("success_login.html", username=username)
                return render_template("incorrect_login.html")
    return render_template("login.html")


@app.route("/logedin")
@login_required
def login_success():
    return render_template("success_login.html")


@app.route("/logout", methods= ["POST"])
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM login_table WHERE username = %s AND password = %s",
                    (username, password)
                )
                account = cur.fetchone()
                try:
                    if account:
                        new_password = request.form.get("new_password", "")
                        cur.execute(
                        "UPDATE login_table SET password = %s WHERE username = %s AND password = %s",
                        (new_password, username, password)
                        )
                        return render_template("update_success.html", username=username)
                except psycopg2.errors.CheckViolation:
                    error_message = "Error! Password needs to be at least 8 symbols."
                    return render_template("incorrect_update.html", error_message=error_message)
    return render_template("update.html")
    
        
if __name__ == "__main__":
    app.run(debug=True)