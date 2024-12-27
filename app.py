from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash , check_password_hash
import os
from datetime import datetime
from pymongo import ObjectId
from config.db import dbs, task_db
from model import User
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key_for_dev")

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user_data = dbs.find_one({"_id" : ObjectId(user_id)})
    if user_data:
        return User(id = str(user_data["_id"]), name = user_data["UserName"],email = user_data["Email"],  password=user_data["Password"])
    return None

@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        task = request.form.get("task")
        if task:
            data = {
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Task": task,
               "UserId": ObjectId(current_user.id)
            }
            task_db.insert_one(data)
            flash("Task added successfully!", category='success')
        else:
            flash("Task cannot be empty", category='error')
    tasks = list(task_db.find({"UserId": current_user.id}))
    return render_template(template_name_or_list="home.html", tasks=tasks )


@app.route("/check_task", methods=['GET', 'POST'])
@login_required
def check_task():
    tasks = list(task_db.find({"UserId": ObjectId(current_user.id)}))
    task_list = [{"id": str(task["_id"]), "Date": task["Date"], "Task": task["Task"]} for task in tasks]
    return render_template(template_name_or_list="home.html", task_list=task_list)



@app.route("/signup",  methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get("name")
        mail = request.form.get("email")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        if not name or not mail or not password:
            flash("All fields are required.", category="error")
        elif dbs.find_one({"Email":mail}):
            flash("Email is in use", category="error")
            return redirect(url_for("signup"))    
        elif dbs.find_one({"UserName":name}):
            flash("Username is in use", category="error")
            return redirect(url_for("signup"))
        elif len(mail) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name)<2:
            flash('First name must be at least 2 characters.', category='error')
        elif len(password)<7:
            flash("Password must be at least 7 characters.", category='error')
        else:
            user = {
            "UserName": name,
            "Email": mail,
            "Password": hashed_password
            }
            dbs.insert_one(user)      
            flash("Account created successfully", category="success")
            return redirect(url_for('login'))
    return render_template(template_name_or_list="signup.html")

@app.route("/login",  methods=['GET', 'POST'])
def login():
    if request.method=="POST":
        name = request.form.get("name")
        password = request.form.get("password")
        user = dbs.find_one({"UserName":name})

        if user and check_password_hash(user["Password"], password):
            login_user(User(id = str(user["_id"]), name = user["UserName"],email = user["Email"],  password=user["Password"]))
            flash("Login successful", category="success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials", category="error")
        
    return render_template(template_name_or_list="login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", category="success")
    return redirect(url_for("login"))


@app.route("/test")
def test():
    if current_user.is_authenticated:
        return f"User is authenticated: {current_user.name}"
    else:
        return "User is not authenticated"

@app.route('/update_task/<task_id>', methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task = task_db.find_one({"_id": ObjectId(task_id), "UserId": ObjectId(current_user.id)}) 
    print(task)
    if not task:
        return "Task not found", 404

    if request.method == 'POST':
        new_task_name = request.form['task']
        task_db.update_one(
            {"_id": ObjectId(task_id), "UserId": ObjectId(current_user.id)},
            {"$set": {"Task": new_task_name,"Date": datetime.now().strftime("%Y-%m-%d")}}
        )
        flash("Task updated successfully.", "success")
        return redirect(url_for('home')) 
    task["_id"] = str(task["_id"])
    flash("Task updated successfully.", "success")
    return render_template('update.html', task=task)


@app.route('/delete_task/<task_id>', methods=["GET",'POST'])
@login_required
def delete_task(task_id):
    result = task_db.delete_one({"_id": ObjectId(task_id), "UserId": ObjectId(current_user.id)})
    if result.deleted_count == 0:
        flash("Task not found or unauthorized access.", "danger")
    else:
        flash("Task deleted successfully.", "success")
    return redirect(url_for('home'))


if __name__=="__main__":
    app.run(debug=True, port=5000)