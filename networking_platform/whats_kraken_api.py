import flask, sys
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from login_user_models import *
from login_forms import *
import boto3 

import os
from pymongo import MongoClient
import pymongo
import mongodb_config as cfg
import aws_config as aws_settings
import checking_file_types
from checking_file_types import verify_PDF_image, verify_valid_image
import database_handling
from database_handling import deleteResume, deleteCoverLetter, getResumeCount, getCoverLetterCount

app = Flask(__name__)
app.secret_key = '123456789'
login = LoginManager(app)
login.init_app(app)

# Establish connection with MongoClient and iniitalize DataBase
client = MongoClient("mongodb+srv://"+ cfg.mongodb["username"] + ":" + cfg.mongodb["password"] + "@" + cfg.mongodb["host"])
userdb = client.Whats_Kraken # the DB name is Whats_Kraken

# Build s3 low-level client for object insertions into s3 bucket, and s3 high-level resource for deleting objects
s3 = boto3.client('s3', aws_access_key_id=aws_settings.aws["ACCESS_KEY_ID"], aws_secret_access_key=aws_settings.aws["SECRET_ACCESS_KEY"], region_name=aws_settings.aws["REGION_NAME"])
s3_resource = boto3.resource('s3', aws_access_key_id=aws_settings.aws["ACCESS_KEY_ID"], aws_secret_access_key=aws_settings.aws["SECRET_ACCESS_KEY"], region_name=aws_settings.aws["REGION_NAME"])

@login.user_loader
def load_user(username):
    
    user = userdb.user_credentials.find_one({"username": username})

    if user is not None:
        found_user = User(user["username"], user["email"], password_hash=user['password'])
        return found_user

    return user

login.login_view='/login'


# BEGIN LOGIN & REGISTRATION ENDPOINTS 

@app.route("/login", methods=["GET", "POST"])
def login_page():
        if current_user.is_authenticated:
                return redirect(url_for('index'))
        form = LoginForm()
        if form.validate_on_submit():
                user = load_user(str(form.username.data))
                if user is None or not user.check_password(form.password.data):
                        flash('Invalid username or password')
                        return redirect(url_for('login_page'))
                
                login_user(user)
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                        next_page = url_for('index')
                return redirect(next_page)

        return render_template('login.html', title='Sign In', form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
        if current_user.is_authenticated:
                return redirect(url_for('index'))
        form = RegistrationForm()
        if form.validate_on_submit():
                fname = request.form.get("fname")
                lname = request.form.get("lname")

                user = User(form.username.data, form.email.data)
                user.set_password(form.password.data)

                userdb.user_credentials.insert_one({"username":user.username, "password":user.password_hash, "email":user.email})
                userdb.user_intro_data.insert_one({"username":user.username, "fname":fname,"lname":lname, "major":"", 
                "class_standing":"", 
                "bio":"",
                "profile_pic":"../static/images/head.png",
                "link_1":"",
                "link_2":"",
                "link_3":""})
                flash('Congratulations, you are now a registered user!')
                userdb.user_resumes.insert_one({"username":user.username, "current_selection_id":{"id":"", "type":""}, "resume_uploads":[], "resume_creations":[]})
                userdb.user_cover_letters.insert_one({"username":user.username, "current_selection_id":{"id":"", "type":""}, "cover_letter_uploads":[], "cover_letter_creations":[]})
                ls = ["../static/images/slide" + str(i) + ".png" for i in range(5)]
                userdb.user_carousels.insert_one({"username":user.username, "carousel1_imgs":ls})
                return redirect(url_for('login_page'))

        return render_template('registration.html', title='Register', form=form)

@app.route("/logout")
def logout():
        logout_user()
        return redirect(url_for('login_page'))

@app.route("/")
@app.route("/index")
def index():
        return render_template("index.html")



# BEGIN INTRODUCTION ENDPOINTS

@app.route("/profile")
@login_required
def profile():

        curr_username = current_user.username
        intro_data = userdb.user_intro_data.find_one({"username":curr_username})
        
        session["user_fullname"] = intro_data["fname"] + " " + intro_data["lname"]

        return render_template("profile.html", intro_data=intro_data)

@app.route("/edit_intro", methods=["POST", "GET"])
@login_required
def edit_intro():

        if request.method == "POST":

                data = request.form
                data_dict = data.to_dict()
                for key in data_dict.keys():
                        val = data_dict[key]
                        userdb.user_intro_data.update_one({ "username": current_user.username}, { "$set": { key : val } })

        return redirect(url_for("profile"))

@app.route("/upload_profile_pic", methods=["POST"])
@login_required
def upload_profile_pic():

        profile_pic = request.files["profile_img"]
        filename = profile_pic.filename

        if verify_valid_image(filename):
                response = {"response":"Success"}
                key = "profile_pictures/" + current_user.username + ".png"
                s3.put_object(Bucket="whats-kraken-images", Body=profile_pic, Key=key, ACL='public-read', ContentType='image/png', CacheControl= "no-cache")
                
                new_profile_pic = "https://whats-kraken-images.s3.us-east-2.amazonaws.com/" + key
                userdb.user_intro_data.update_one({ "username": current_user.username}, { "$set": { "profile_pic" : new_profile_pic } })
        elif filename == "":
                response = {"response":"Empty"}
        else:
                response = {"response":"Invalid_Format"}
        return response


# BEGIN RESUME ENDPOINTS 

@app.route("/resume", methods=["POST","GET"])
@login_required
def resume():
        
        data = userdb.user_resumes.find_one({"username":current_user.username})
        if data == None:
                user_resumes = {"resume_uploads":[], "resume_creations":[]}
        else:
                user_resumes = {"resume_uploads":data["resume_uploads"], "resume_creations":data["resume_creations"]}

        return render_template("resume.html", user_resumes=user_resumes)

@app.route("/resume_upload", methods=["POST", "GET"])
@login_required
def resume_upload():

        curr_username = current_user.username

        resume_file = request.files["res_upload"]
        filename = resume_file.filename
        resume_cnt_bool = getResumeCount("uploads", curr_username, userdb) >= 3

        if not verify_PDF_image(filename) or resume_file == None:
                response = {"response": "Failed"}
        elif resume_cnt_bool:
                response = {"response": "Max_Uploads"}
        else:
                key = "resumes/" + curr_username + "/" + filename
                s3.put_object(Bucket="whats-kraken-images", Body=resume_file, Key=key, ACL='public-read', ContentType='application/pdf')
                
                new_resume = "https://whats-kraken-images.s3.us-east-2.amazonaws.com/" + key

                resume_details = {"aws_link":new_resume, "key":key, "filename":filename}
                userdb.user_resumes.update_one({ "username": current_user.username}, {"$push":{"resume_uploads": resume_details}})
                response = {"response": "Success"}

        return response

@app.route("/delete_uploaded_resume", methods=["POST"])
@login_required
def delete_uploaded_resume():

        form_data = request.form 
        form_data_dict = form_data.to_dict()
        resume_key = form_data_dict["resume_key"]
        
        deleteResume("uploads", resume_key, current_user.username, userdb)

        obj = s3_resource.Object("whats-kraken-images", resume_key)
        obj.delete()

        return {"response":"Deletion Successful"}


@app.route("/resume_create", methods=["POST","GET"])
@login_required
def build_resume():

        if request.method == "POST":

                data = request.form
                data_dict = data.to_dict()

                resume_cnt_bool = getResumeCount("creations", current_user.username, userdb) >= 3
                if resume_cnt_bool:
                        response = {"response":"Max_Uploads"}
                else:
                        userdb.user_resumes.update_one({ "username": current_user.username}, { "$push": { "resume_creations" : data_dict } })
                        response = {"response":"Success"}

        return response

@app.route("/resume_preview/<resume_title>", methods=["POST", "GET"])
@login_required
def resume_preview(resume_title):

        data = userdb.user_resumes.find_one({"username": current_user.username})
        resume_creations = data["resume_creations"]
        resume_data = {}
        for resume in resume_creations:
                if resume["title"] == resume_title:
                        resume_data = resume
                
        return render_template("resume_preview.html", resume_data=resume_data)

@app.route("/delete_created_resume", methods=["POST", "GET"])
@login_required
def delete_created_resume():

        form_data = request.form 
        form_data_dict = form_data.to_dict()
        resume_key = form_data_dict["resume_key"]
        deleteResume("creations", resume_key, current_user.username, userdb)

        return {"response":"Deletion Successful"}

@app.route("/resume_edit", methods=["POST", "GET"])
@login_required
def edit_resume():

        form_data = request.form 
        data_dict = form_data.to_dict()
        resume_key = data_dict["title"]
        try:
                deleteResume("creations", resume_key, current_user.username, userdb)
                userdb.user_resumes.update_one({ "username": current_user.username}, { "$push": { "resume_creations" : data_dict } })
                response={"response":"Success"}
        except:
                print("Unable to update resume")
                response = {"response":"Unable to update resume"}

        return response

@app.route("/resume_select_default", methods=["POST","GET"])
def resume_select():

        data = request.form.to_dict()
        key = data["resume_key"]
        res_type = data["resume_type"]
        try:
                userdb.user_resumes.update_one({"username":current_user.username}, {"$set": {"current_selection_id":{"id":key, "type":res_type}}})
                response={"response":"Success"}
        except:
                response = {"response":"Failed"}

        return response



# BEGIN COVER LETTER ENDPOINTS

@app.route("/cover_letter", methods=["POST","GET"])
@login_required
def cover_letter():

        data = userdb.user_cover_letters.find_one({"username":current_user.username})
        if data == None:
                user_cover_letters = {"cover_letter_uploads":[], "cover_letter_creations":[]}
        else:
                user_cover_letters = {"cover_letter_uploads":data["cover_letter_uploads"], "cover_letter_creations":data["cover_letter_creations"]}

        return render_template("coverletter.html", user_cover_letters=user_cover_letters)

@app.route("/cover_letter_upload", methods=["POST", "GET"])
@login_required
def cover_letter_upload():

        curr_username = current_user.username

        cover_letter = request.files["cover_letter_upload"]
        filename = cover_letter.filename
        cl_cnt_bool = getCoverLetterCount("uploads", curr_username, userdb) >= 3

        if not verify_PDF_image(filename) or cover_letter == None:
                response = {"response": "Invalid_Format"}
        elif cl_cnt_bool:
                response = {"response": "Max_Uploads"}
        else:
                key = "cover_letters/" + curr_username + "/" + filename
                s3.put_object(Bucket="whats-kraken-images", Body=cover_letter, Key=key, ACL='public-read', ContentType='application/pdf')
                
                new_resume = "https://whats-kraken-images.s3.us-east-2.amazonaws.com/" + key

                resume_details = {"aws_link":new_resume, "key":key, "filename":filename}
                userdb.user_cover_letters.update_one({ "username": current_user.username}, {"$push":{"cover_letter_uploads": resume_details}})
                response = {"response": "Success"}

        return response

@app.route("/delete_uploaded_cover_letter", methods=["POST"])
@login_required
def delete_uploaded_cover_letter():

        form_data = request.form 
        form_data_dict = form_data.to_dict()
        cl_key = form_data_dict["cover_letter_key"]
        
        deleteCoverLetter("uploads", cl_key, current_user.username, userdb)
        try:
                obj = s3_resource.Object("whats-kraken-images", cl_key)
                obj.delete()
                response = {"response":"Deletion Successful"}
        except:
                response = {"response":"Deletion Failed"}

        return response

@app.route("/cover_letter_create", methods=["POST","GET"])
@login_required
def build_cover_letter():

        if request.method == "POST":

                data = request.form
                data_dict = data.to_dict()

                cl_cnt_bool = getCoverLetterCount("creations", current_user.username, userdb) >= 3
                if cl_cnt_bool:
                        response = {"response":"Max_Uploads"}
                else:
                        userdb.user_cover_letters.update_one({ "username": current_user.username}, { "$push": { "cover_letter_creations" : data_dict } })
                        response = {"response":"Success"}

        return response

@app.route("/delete_created_cover_letter", methods=["POST", "GET"])
@login_required
def delete_created_cover_letter():

        form_data = request.form 
        form_data_dict = form_data.to_dict()
        cl_key = form_data_dict["cl_key"]
        deleteCoverLetter("creations", cl_key, current_user.username, userdb)

        return {"response":"Deletion Successful"}

@app.route("/cover_letter_preview/<cl_title>", methods=["POST", "GET"])
@login_required
def cover_letter_preview(cl_title):

        data = userdb.user_cover_letters.find_one({"username": current_user.username})
        cl_creations = data["cover_letter_creations"]
        cl_data = {}

        for cl in cl_creations:
                if cl["title"] == cl_title:
                        cl_data = cl
                
        return render_template("cover_letter_preview.html", cl_data=cl_data)

@app.route("/cover_letter_edit", methods=["POST", "GET"])
@login_required
def cover_letter_edit():

        form_data = request.form 
        data_dict = form_data.to_dict()
        cl_key = data_dict["title"]
        try:
                deleteCoverLetter("creations", cl_key, current_user.username, userdb)
                userdb.user_cover_letters.update_one({ "username": current_user.username}, { "$push": { "cover_letter_creations" : data_dict } })
                response={"response":"Success"}
        except:
                print("Unable to update resume")
                response = {"response":"Unable to update cover letter"}

        return response

@app.route("/cover_letter_select_default", methods=["POST","GET"])
def cover_letter_select():

        data = request.form.to_dict()
        key = data["cover_letter_key"]
        cl_type = data["cover_letter_type"]
        try:
                userdb.user_cover_letters.update_one({"username":current_user.username}, {"$set": {"current_selection_id":{"id":key, "type":cl_type}}})
                response={"response":"Success"}
        except:
                response = {"response":"Failed"}

        return response


# BEGIN MY LIFE ENDPOINTS

@app.route("/my_life", methods=["POST","GET"])
@login_required
def my_life():
        curr_username = current_user.username
        carousels = userdb.user_carousels.find_one({"username":curr_username})
        
        return render_template("my_life.html", carousels= carousels)

@app.route("/upload_mylife_pic", methods=["POST"])
@login_required
def upload_mylife_pic():

        imgs = request.files.to_dict()

        success = True
        
        for index in imgs.keys():
                
                mylife_pic = imgs[index]
                filename = mylife_pic.filename
                if filename != "":

                        if verify_valid_image(filename):
                        
                                try:  
                                        key = "mylife_pictures/" + current_user.username + "/" + filename
                                        s3.put_object(Bucket="whats-kraken-images", Body=mylife_pic, Key=key, ACL='public-read', ContentType='image/png', CacheControl= "no-cache")
                                        new_mylife_pic = "https://whats-kraken-images.s3.us-east-2.amazonaws.com/" + key
                                        userdb.user_carousels.update_one({ "username": current_user.username}, { "$set": { "carousel1_imgs."+index: new_mylife_pic }})
                                except:
                                        success = False
                                        print("Failed in Try Except")

                        else:
                                success = False
                                print("Failed in File Format")


        if success:
                response = {"response": "Success"}
        else:
                response = {"response": "Failed"}

        return response


# BEGIN MEMBER ENDPOINTS

@app.route("/members")
def members():
    names = userdb.user_intro_data.find({}, {"fname": 1})
    images = userdb.user_intro_data.find({}, {"profile_pic": 1})
    bios = userdb.user_intro_data.find({}, {"bio": 1})
    majors = userdb.user_intro_data.find({}, {"major": 1})
    classStandings = userdb.user_intro_data.find({}, {"class_standing": 1})
    usernames = userdb.user_intro_data.find({}, {"username": 1})
    firstNames = list(map(lambda name: name["fname"] if "fname" in name else "", list(names)))
    names = userdb.user_intro_data.find({}, {"lname": 1})
    lastNames = list(map(lambda name: name["lname"] if "lname" in name else "", list(names)))
    names = list(map(lambda fname, lname: fname + " " + lname if fname != "" or lname != "" else "NO NAME", firstNames, lastNames))
    bios = list(map(lambda bio: bio["bio"] if "bio" in bio else "", list(bios)))
    images = list(map(lambda image: image["profile_pic"] if "profile_pic" in image else "../project2/static/images/default_profile_img.png",
                      list(images)))
    majors = list(map(lambda major: major["major"] if "major" in major else "N/A", list(majors)))
    classStandings = list(map(lambda classStanding: classStanding["class_standing"] if "class_standing" in classStanding else "N/A", classStandings))
    usernames = list(map(lambda username: username["username"], list(usernames)))
    
    return render_template("members.html", names=names, bios=bios, images=images, majors=majors, classStandings=classStandings, usernames=usernames)


@app.route("/member_profiles/<username>")
def user_profiles(username):


        intro_data = userdb.user_intro_data.find_one({"username":username})
        if intro_data != None:
                session["user_fullname"] = intro_data["fname"] + " " + intro_data["lname"]
                session["view_member"] = username
        else:
                session["user_fullname"] = ""
                session["view_member"] = ""
                intro_data = {}

        return render_template("user_profile.html", intro_data=intro_data)

@app.route("/member_resumes/<username>", methods=["POST","GET"])
def user_resumes(username):
    
        data = userdb.user_resumes.find_one({"username":username})
        if data == None:
                res_data = {"res_type":"", "res_data":""}
        else:
                key = data["current_selection_id"]["id"]
                res_type = data["current_selection_id"]["type"]
                if (res_type != "") and (key != ""):

                        member_resumes = data[res_type]
                        for res in member_resumes:
                                if res_type == "resume_creations":
                                        if res["title"] == key:
                                                member_res = res
                                elif res_type == "resume_uploads":
                                        if res["key"] == key:
                                                member_res = res["aws_link"]

                        res_data = {"res_type":res_type, "res_data":member_res}
                        
                else:
                        res_data = {"res_type":"", "res_data":""}

        return render_template("user_resume.html", resume_data=res_data)

@app.route("/member_cover_letters/<username>", methods=["POST","GET"])
def user_cover_letter(username):

        data = userdb.user_cover_letters.find_one({"username":username})
        if data == None:
                cl_data = {"cl_type":"", "cl_data":""}
        else:
                key = data["current_selection_id"]["id"]
                cl_type = data["current_selection_id"]["type"]
                if (cl_type != "") and (key != ""):

                        member_cover_letters = data[cl_type]
                        for cl in member_cover_letters:
                                if cl_type == "cover_letter_creations":
                                        if cl["title"] == key:
                                                member_cl = cl
                                elif cl_type == "cover_letter_uploads":
                                        if cl["key"] == key:
                                                member_cl = cl["aws_link"]

                        cl_data = {"cl_type":cl_type, "cl_data":member_cl}
                        
                else:
                        cl_data = {"cl_type":"", "cl_data":""}

        return render_template("user_coverletter.html", cl_data=cl_data)

@app.route("/member_my_life/<username>", methods=["POST","GET"])
def user_my_life(username):
    curr_username = username
    carousels = userdb.user_carousels.find_one({"username":curr_username})
        
    return render_template("user_my_life.html", carousels= carousels)

    
@app.route("/Kraken")
def Kraken():
        return render_template("Kraken.html")

    
if __name__ == "__main__":
    app.run(debug=True, port=5000)
