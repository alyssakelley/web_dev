import flask, sys
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from login_user_models import *
from login_forms import *

import os
from pymongo import MongoClient
import pymongo
import mongodb_config as cfg

app = Flask(__name__)
app.secret_key = '123456789'
login = LoginManager(app)
login.init_app(app)

@login.user_loader
def load_user(username):
    
    user = userdb.AddressBook_Users.find_one({"username": username})

    if user is not None:
        found_user = User(user["username"], password_hash=user['password'])
        return found_user

    return user

login.login_view='/login'

# Establish connection with MongoClient and iniitalize DataBase
client = MongoClient("mongodb+srv://"+ cfg.mongodb["username"] + ":" + cfg.mongodb["password"] + "@" + cfg.mongodb["host"])
userdb = client.Users # the DB name is Users

# temporarily store all contacts being added to an address book until a user selects "Save" (which sends the 
# all new contacts to the DB).

contacts_to_delete = dict()
new_contacts = dict()
edited_contacts = dict()


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
                user = User(form.username.data)
                user.set_password(form.password.data)
                userdb.AddressBook_Users.insert({"username":user.username, "password":user.password_hash})
                flash('Congratulations, you are now a registered user!')
                return redirect(url_for('login_page'))

        return render_template('registration.html', title='Register', form=form)

@app.route("/logout")
def logout():
        logout_user()
        return redirect(url_for('login_page'))

@app.route("/")
@app.route("/index")
@login_required
def index():

        contact_books = userdb.Address_Books.find({"user":current_user.username})
        address_book_names = []
        if contact_books != None:
                for document in contact_books:
                        address_book_names.append(document["book_name"])

        session["address_book_names"] = address_book_names

        return render_template("home.html")

@app.route("/addnew", methods=["POST", "GET"])
@login_required
def addnew():

        title = request.form.get("title")
        session["title"] = title

        return render_template("addnew.html")


@app.route("/openExisting/<book_name>", methods=["POST", "GET"])
@login_required
def getAddressBook(book_name):

        contact_book = userdb.Address_Books.find_one({"user":current_user.username, "book_name":book_name})
        contacts = []
        
        if contact_book != None:

                contacts = contact_book["contacts"]
                session["title"] = contact_book["book_name"]
        else:
                print("Oops, couldn't find the book!")

        return render_template("addnew.html", contacts=contacts)

@app.route("/_addContact", methods=["POST", "GET"])
@login_required
def _addContact():

        global new_contacts
        if request.method == "POST":

                first_name = request.form.get("first_name")
                last_name = request.form.get("last_name")
                phone_num = request.form.get("phone_num")
                address = request.form.get("address")
                city = request.form.get("city")
                state = request.form.get("state")
                zipcode = request.form.get("zipcode")
                id_num = request.form.get("id")
                email = request.form.get("email")
                
                contact = {"fname":first_name, "lname":last_name, "phone":phone_num, "email":email , "address":address, "city":city, "state":state, "zipcode":zipcode, "id_num":id_num}
                new_contacts[id_num] = contact
                 
        return redirect(url_for("addnew"))


#Method for deleting by index inspired by https://stackoverflow.com/questions/4588303/in-mongodb-how-do-you-remove-an-array-element-by-its-index

@app.route("/_editContact", methods=["POST", "GET"])
@login_required
def _editContact():

        global new_contacts
        if request.method == "POST":
                first_name = request.form.get("first_name")
                last_name = request.form.get("last_name")
                phone_num = request.form.get("phone_num")
                address = request.form.get("address")
                city = request.form.get("city")
                state = request.form.get("state")
                zipcode = request.form.get("zipcode")
                ide = request.form.get("id")
                email = request.form.get("email")

                updated_contact = {"fname":first_name, "lname":last_name, "phone":phone_num, "email":email, "address":address, "city":city, "state":state, "zipcode":zipcode, "id_num":ide}
                
                #print("\nORIGINAL CONTACTS:", new_contacts, "\n")
                #print("\nUPDATED CONTACT: ", updated_contact, "\n")

                if not bool(new_contacts) or (bool(new_contacts) and (ide not in new_contacts.keys())):
                        edited_contacts[ide] = updated_contact
                else:
                        try:
                                new_contacts[ide] = updated_contact
                        except KeyError as e:
                                print(e)

                #print("UPDATED CONTACTS DICT: ", new_contacts, "\n")
        return redirect(url_for("addnew"))

def deleteContactDB(query, id_num):
    array_name = "contacts"
    array_item_name = "id_num"
    return userdb.Address_Books.update_one(query, {"$pull" : {array_name : {array_item_name : id_num}}})

@app.route("/deleteContact", methods=["POST", "GET"])
@login_required
def deleteContact():
    if request.method == "POST":
        print("before get")
        id_num = request.form.get("id")
        print("after get")
        #We really just need the key to see if the id_num is in the database
        #So we just need to store that
        if id_num in edited_contacts:
            edited_contacts.pop(id_num)
        
        if id_num in new_contacts:
            new_contacts.pop(id_num)
        
        contacts_to_delete[id_num] = id_num

    return redirect(url_for("addnew"))
        
@app.route("/<book_type>/save", methods=["POST", "GET"])
@login_required
def save(book_type):

        global new_contacts, edited_contacts, contacts_to_delete
        book_name = request.form.get("book_name")
        address_book_exists = userdb.Address_Books.find_one({"user":current_user.username, "book_name":book_name})

        if address_book_exists == None:
                # This is a new address book, as we can't find it in the DB. Thus, create a new address book with all newly created 
                # contacts and insert it as a fresh collection. 
                address_book = dict()
                address_book["contacts"] = []
                address_book["user"] = current_user.username
                address_book["book_name"] = request.form.get("book_name")
                for contact in new_contacts.values():
                        address_book["contacts"].append(contact)
                
                new_contacts = dict()
                userdb.Address_Books.insert_one(address_book)
                print("\n A new Address Book for " + current_user.username + " has been added to the database.\n")
        else:
                # The user is adding to/editing contacts in an existing address book. Hence, we use the pymongo 'update_one' method. 
                for contact in new_contacts.values():
                        userdb.Address_Books.update_one({"user":current_user.username, "book_name":book_name}, {"$push":{"contacts": contact}})
                        
                for updated_contact in edited_contacts.values():
                        ide = updated_contact["id_num"]
                        userdb.Address_Books.update_one({ "user": current_user.username, "book_name":book_name, "contacts.id_num": ide }, { "$set": { "contacts.$" : updated_contact } })

                for delete_contact in contacts_to_delete.values():
                        deleteContactDB({ "user": current_user.username, "book_name":book_name, "contacts.id_num": delete_contact }, delete_contact)
                        
                new_contacts = dict()
                edited_contacts = dict()

                contacts_to_delete = dict()
        
        return redirect(url_for(book_type))

@app.route("/<book_type>/delete", methods=["POST", "GET"])
@login_required
def delete_book(book_type):
    global new_contacts, edited_contacts, contacts_to_delete
    book_name = request.form.get("book_name")
    address_book_exists = userdb.Address_Books.find_one({"user":current_user.username, "book_name":book_name})

    if address_book_exists:
        # This is a new address book, as we can't find it in the DB. Thus, create a new address book with all newly created 
        # contacts and insert it as a fresh collection. 
        userdb.Address_Books.delete_one({"user":current_user.username, "book_name":book_name})
    return redirect(url_for("index"))
    
if __name__ == "__main__":
    #TESTING DELETE
    """contacts_to_delete["2"] = "2"
    
    for delete_contact in contacts_to_delete.values():
       print(deleteContactDB({ "user": "ttest", "book_name":"test1", "contacts.id_num": delete_contact }, delete_contact).raw_result)"""
                    
    #END TESTING DELETE
    app.run(debug=True, port=5000)
