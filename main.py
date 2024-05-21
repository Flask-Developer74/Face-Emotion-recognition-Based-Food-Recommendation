
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, Response
import gunicorn
import mysql.connector
from camera import *
import csv

app = Flask(__name__)

headings = ("Name","Album","Artist")
df1 = music_rec()
df1 = df1.head(15)

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'abcdef'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    charset="utf8",
    database="emotion_food"
)


@app.route('/')
def index():
    
    return render_template('index.html')


@app.route('/admin',methods=['POST','GET'])
def admin():
    
    
    msg=""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        
        if account:
            session['username'] = username
            session['user_type'] = 'admin'
            msg="success"
        else:
            msg="fail"
        

    return render_template('admin.html',msg=msg)



@app.route('/login',methods=['POST','GET'])
def login():
    
    
    msg=""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s AND action=1 ', (username, password))
        account = cursor.fetchone()
        
        if account:
            session['username'] = username
            session['user_type'] = 'user'
            msg="success"
        else:
            msg="fail"
        

    return render_template('login.html',msg=msg)


@app.route('/regsiter',methods=['POST','GET'])
def regsiter():
    msg=""
    st=""
    name=""
    email=""
    mess=""
    reg_no=""
    password=""
    if request.method=='POST':

        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        address=request.form['address']
        username=request.form['username']
        password=request.form['password']

        
        now = datetime.datetime.now()
        date_join=now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()

        mycursor.execute("SELECT count(*) FROM user where username=%s",(username, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM user")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
            sql = "INSERT INTO user(id, name, mobile, email, address, username, password,date_join) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = (maxid, name, mobile, email, address, username, password,date_join)
            mycursor.execute(sql, val)
            mydb.commit()

            msg="success"
            st="1"
            mess = f"Reminder: Hi {name}, your username is {reg_no} and password is {password}!"
            mycursor.close()
        else:
            msg="fail"
            
    return render_template('regsiter.html', msg=msg)


@app.route('/user_request',methods=['POST','GET'])
def user_request():
    
    if 'username' not in session or session.get('user_type') != 'admin':
        print("Please log in as a hod to access the page.", 'danger')
        return redirect(url_for('admin'))
    
    act=request.args.get("act")
    username = session.get('username')
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM user")
    data1 = cursor.fetchall()
    cursor.close()

    if act=="ok":
        uid=request.args.get("uid")
        cursor = mydb.cursor()
        cursor.execute("update user set action=1 where id=%s",(uid,))
        mydb.commit()
        print("successfully accepted")
        
    if act=="no":
        uid=request.args.get("uid")
        cursor = mydb.cursor()
        cursor.execute("update user set action=2 where id=%s",(uid,))
        mydb.commit()
        print("your account will be rejected")


    return render_template('user_request.html', user=data1)




@app.route('/edit', methods=['GET', 'POST'])
def edit():
    msg=""
    data=[]
    df=pd.read_csv('songs/angry.csv')
    dat=df.head(100)

    for ss in dat.values:
        data.append(ss)


    df1=pd.read_csv('songs/disgusted.csv')
    dat1=df1.head(100)

    for ss1 in dat1.values:
        data.append(ss1)


    df2=pd.read_csv('songs/fearful.csv')
    dat2=df2.head(100)

    for ss2 in dat2.values:
        data.append(ss2)


    df3=pd.read_csv('songs/happy.csv')
    dat3=df3.head(100)

    for ss3 in dat3.values:
        data.append(ss3)


    df4=pd.read_csv('songs/neutral.csv')
    dat4=df4.head(100)

    for ss4 in dat4.values:
        data.append(ss4)

    df5=pd.read_csv('songs/sad.csv')
    dat5=df5.head(100)

    for ss5 in dat5.values:
        data.append(ss5)

    


    
    
    return render_template('edit.html',data=data)



def append_to_csv(data):
    csv_file = 'D:/Expression_food/songs/angry.csv'  # Path to your CSV file
    
    # Append data to CSV file
    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)


        
@app.route('/add_food', methods=['POST', 'GET'])
def add_food():

    msg = ""
    if request.method == 'POST':
        # Retrieve form data
        emotion=request.form['emotion']
        food = request.form['food']
        
        

        # Prepare data to append to CSV file
        patient_data = [emotion, food]

        # Call function to append data to CSV
        append_to_csv(patient_data)
        msg = "success"

    return render_template('add_food.html', msg=msg)





@app.route('/test')
def test():
    print(df1.to_json(orient='records'))
    return render_template('test.html', headings=headings, data=df1)

def gen(camera):
    while True:
        global df1
        frame, df1 = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/t')
def gen_table():
    return df1.to_json(orient='records')



@app.route('/logout')
def logout():
    session.clear()
    print("Logged out successfully", 'success')
    return redirect(url_for('index'))





if __name__ == '__main__':
    app.debug = True
    app.run()
