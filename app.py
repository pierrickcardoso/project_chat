from flask import Flask, render_template,request,redirect, url_for,session
from outils_sql import *
import bcrypt
requete_ajouter_user = "INSERT INTO 'user' (username,password) VALUES (?, ?);"
requete_ajouter_message ="INSERT INTO 'text' (sender,receiver,contenue) VALUES (?, ?,?);"
requete_lire_user = "SELECT * FROM 'user' "
requete_lire_user_only = "SELECT username FROM 'user' "
requete_lire_text = "SELECT * FROM 'text' "
requete_lire_pm = "select * from text where receiver ="
app = Flask(__name__)
bdd="BDD.db"
Currentuser = None
sel=b'$2b$12$nPN1vKLICBRm2KDglXEe7u'
app.secret_key=b"$2b$12$nPN1vKLICBRm2KDglXEe7ufW9wct2kv7b7g/jWVwCbqRycdM0sYSG"
@app.route("/")
def index():
    return render_template("index.html", var_sign_in = url_for('s_inscrire'), var_log_in=url_for('login'))

@app.route("/s_inscrire")
def s_inscrire():
     return render_template("s_inscrire.html")
@app.route('/recup_donnees_user', methods=['POST'])
def recup_donnees_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode("utf-8")
        password= bcrypt.hashpw(password,sel)
        liste_user=lire(bdd,requete_lire_user_only,multiples=True)
        for elem in liste_user:
            if username in elem:
                return redirect(url_for('index'))
        if username and password != None:
            modifier(bdd,requete_ajouter_user,parametres=(username,password))
    return redirect(url_for('index'))
@app.route("/login")
def login():
    return render_template("login.html",var_retour=url_for('index'))

@app.route("/verif_user", methods=['POST'])
def verif_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode("utf-8")
        liste_user=lire(bdd,requete_lire_user,multiples=True)
        for elem in liste_user:
            if elem[0] == username:
                if bcrypt.hashpw(password,sel)==elem[1]:
                    session['username']=elem[0]
                    return redirect(url_for('succes'))
        return redirect(url_for('index'))
@app.route("/succes")
def succes():
    if session['username']==None:
        return redirect(url_for('index'))
    temp=lire(bdd,requete_lire_text,multiples=True)
    res=[]
    for elem in temp:
        if elem[1]=="all":
            res.append(elem)    
    return render_template("succes.html",message=res,var_deconnexion=url_for('logout'))
@app.route("/send_message", methods=['POST'])
def send_message():
    text=request.form['text']
    modifier(bdd,requete_ajouter_message,parametres=(session['username'],"all",text))
    return redirect(url_for('succes'))
@app.route('/logout')
def logout():
    session['username']=None
    session['receiver']=None
    return redirect(url_for('index'))
@app.route("/get_receiver", methods=['POST'])
def get_receiver():
    sender=session['username']
    receiver=request.form['text']
    if receiver==sender or receiver==None:
        redirect(url_for('succes'))
    session['receiver']=receiver
    return redirect(url_for('private_msg'))
@app.route("/private_msg")
def private_msg():
    requete_temp=requete_lire_pm+"'"+session['receiver']+"'"
    print(requete_temp)
    result=lire(bdd,requete_lire_text,multiples=True)
    print(result)
    return render_template("private_msg.html",message=result ,var_deconnexion=url_for('logout'), var_chat_global=url_for('succes'))
@app.route("/send_private_message", methods=['POST'])
def send_private_message():
    text=request.form['text']
    modifier(bdd,requete_ajouter_message,parametres=(session['username'],session['receiver'],text))
    return redirect(url_for('private_msg'))
if __name__ == '__main__':
    app.run(debug=True, port=8888)
