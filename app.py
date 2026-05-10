# app.py

"""
pip install flask scikit-learn numpy


"""




from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os
from functools import wraps
from datetime import datetime

from sklearn.ensemble import RandomForestRegressor
import numpy as np
import pickle



app = Flask(__name__)
app.secret_key = "greensense_secret_key"

baseDir = os.path.abspath(os.path.dirname(__file__))
dbPath = os.path.join(baseDir, "systemdata.db")

modelPath = os.path.join(baseDir, "temperatureModel.pkl")


def getDbConnection():
    """
    Create sqlite database connection.
    returns: sqlite connection object
    """
    try:
        connection = sqlite3.connect(dbPath)
        connection.row_factory = sqlite3.Row
        return connection

    except Exception as error:
        print(f"error | database connection failed | app.py | {error}")
        return None


def initDatabase():
    """
    Create required tables if not exists.
    """
    try:
        connection = getDbConnection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS userdata (
                userid INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT DEFAULT '*',
                password TEXT DEFAULT '*',
                status TEXT DEFAULT 'active',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logdata (
                logid INTEGER PRIMARY KEY AUTOINCREMENT,
                devicename TEXT DEFAULT 'device123',
                tempval REAL DEFAULT 0.0,
                humval REAL DEFAULT 0.0,
                soilmoistureval REAL DEFAULT 0.0,
                rainval INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notify (
                nid INTEGER PRIMARY KEY AUTOINCREMENT,
                msg TEXT DEFAULT '*',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()
        connection.close()

    except Exception as error:
        print(f"error | init database failed | app.py | {error}")


def loginRequired(routeFunction):
    """
    Check user session before route access.
    """
    @wraps(routeFunction)
    def wrappedFunction(*args, **kwargs):

        if not session.get("username"):
            return redirect("/login")

        return routeFunction(*args, **kwargs)

    return wrappedFunction


@app.route("/")
@loginRequired
def homePage():
    """
    Home dashboard route.
    """
    try:
        connection = getDbConnection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM logdata
            ORDER BY logid DESC
            LIMIT 1
        """)

        latestLog = cursor.fetchone()

        connection.close()

        return render_template(
            "welcome.html",
            latestLog=latestLog
        )

    except Exception as error:
        print(f"error | home page failed | app.py | {error}")
        return "Internal Server Error"


@app.route("/login", methods=["GET", "POST"])
def loginPage():
    """
    Login route.
    """
    try:

        if session.get("username"):
            session.clear()

        if request.method == "POST":

            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            connection = getDbConnection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT *
                FROM userdata
                WHERE username = ?
                AND password = ?
                AND status = 'active'
            """, (username, password))

            userData = cursor.fetchone()

            connection.close()

            if userData:
                session["username"] = username
                return redirect("/")

            return render_template(
                "login.html",
                errorMessage="Invalid credentials"
            )

        return render_template("login.html")

    except Exception as error:
        print(f"error | login failed | app.py | {error}")
        return "Internal Server Error"


@app.route("/register", methods=["GET", "POST"])
def registerPage():
    """
    Register route.
    """
    try:

        if session.get("username"):
            session.clear()

        if request.method == "POST":

            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            connection = getDbConnection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT *
                FROM userdata
                WHERE username = ?
            """, (username,))

            existingUser = cursor.fetchone()

            if existingUser:
                connection.close()

                return render_template(
                    "register.html",
                    errorMessage="Username already exists"
                )

            cursor.execute("""
                INSERT INTO userdata (
                    username,
                    password
                )
                VALUES (?, ?)
            """, (username, password))

            connection.commit()
            connection.close()

            session["username"] = username

            return redirect("/")

        return render_template("register.html")

    except Exception as error:
        print(f"error | register failed | app.py | {error}")
        return "Internal Server Error"


@app.route("/logout")
@loginRequired
def logoutPage():
    """
    Logout route.
    """
    try:
        session.clear()
        return redirect("/login")

    except Exception as error:
        print(f"error | logout failed | app.py | {error}")
        return "Internal Server Error"


@app.route("/logdata")
@loginRequired
def logDataPage():
    """
    Show all logs.
    """
    try:
        connection = getDbConnection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM logdata
            ORDER BY logid DESC
        """)

        allLogs = cursor.fetchall()

        connection.close()

        return render_template(
            "rawlogview.html",
            allLogs=allLogs
        )

    except Exception as error:
        print(f"error | logdata failed | app.py | {error}")
        return "Internal Server Error"


@app.route("/notify")
@loginRequired
def notifyPage():
    """
    Show notifications.
    """
    try:
        connection = getDbConnection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM notify
            ORDER BY nid DESC
        """)

        notifyData = cursor.fetchall()

        connection.close()

        return render_template(
            "notification.html",
            notifyData=notifyData
        )

    except Exception as error:
        print(f"error | notify page failed | app.py | {error}")
        return "Internal Server Error"


@app.route("/aboutus")
@loginRequired
def aboutUsPage():
    """
    About page.
    """
    try:
        return render_template("aboutus.html")

    except Exception as error:
        print(f"error | aboutus failed | app.py | {error}")
        return "Internal Server Error"


@app.route("/profile")
@loginRequired
def profilePage():
    """
    Profile page.
    """
    try:
        connection = getDbConnection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM userdata
            WHERE username = ?
        """, (session.get("username"),))

        userData = cursor.fetchone()

        connection.close()

        return render_template(
            "profile.html",
            userData=userData
        )

    except Exception as error:
        print(f"error | profile page failed | app.py | {error}")
        return "Internal Server Error"


@app.route("/addlog")
def addLogApi():
    """
    Add sensor log using GET request.
    """
    try:

        deviceName = request.args.get("devicename", "device123")
        tempVal = float(request.args.get("tempval", 0.0))
        humVal = float(request.args.get("humval", 0.0))
        soilMoistureVal = float(request.args.get("soilmoistureval", 0.0))
        rainVal = int(request.args.get("rainval", 0))

        connection = getDbConnection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO logdata (
                devicename,
                tempval,
                humval,
                soilmoistureval,
                rainval
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            deviceName,
            tempVal,
            humVal,
            soilMoistureVal,
            rainVal
        ))

        connection.commit()
        connection.close()

        return jsonify({
            "status": "success",
            "message": "log added"
        })

    except Exception as error:
        print(f"error | addlog api failed | app.py | {error}")

        return jsonify({
            "status": "failed",
            "message": str(error)
        })
        
        
@app.route("/apiguide")
@loginRequired
def apiGuidePage():
    """
    API guide page.
    """
    try:

        apiExamples = [
            {
                "title": "Add Sensor Log",
                "method": "GET",
                "endpoint": "/addlog",
                "example": "/addlog?devicename=device123&tempval=28.5&humval=70&soilmoistureval=55&rainval=0",
                "description": "Add live sensor monitoring data into the system."
            }
        ]

        return render_template(
            "apiguide.html",
            apiExamples=apiExamples
        )

    except Exception as error:
        print(f"error | api guide page failed | app.py | {error}")
        return "Internal Server Error"
        
        




def trainTemperatureModel():
    """
    Train Random Forest model using all historical sensor data.
    """

    try:

        connection = getDbConnection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM logdata
            ORDER BY logid ASC
        """)

        allLogs = cursor.fetchall()

        connection.close()

        if len(allLogs) < 20:
            return {
                "status": False,
                "message": "minimum 20 records required"
            }

        featureData = []
        targetData = []

        for row in allLogs:

            try:

                rowTime = datetime.strptime(
                    row["timestamp"],
                    "%Y-%m-%d %H:%M:%S"
                )

                featureData.append([
                    rowTime.hour,
                    rowTime.weekday(),
                    float(row["humval"]),
                    float(row["soilmoistureval"]),
                    int(row["rainval"])
                ])

                targetData.append(
                    float(row["tempval"])
                )

            except Exception as rowError:
                print(f"error | row processing failed | app.py | {rowError}")

        xTrain = np.array(featureData)
        yTrain = np.array(targetData)

        model = RandomForestRegressor(
            n_estimators=300,
            max_depth=15,
            random_state=42
        )

        model.fit(xTrain, yTrain)

        with open(modelPath, "wb") as modelFile:
            pickle.dump(model, modelFile)

        return {
            "status": True,
            "message": f"model trained successfully using {len(featureData)} records"
        }

    except Exception as error:
        print(f"error | train model failed | app.py | {error}")

        return {
            "status": False,
            "message": str(error)
        }
        

@app.route("/trainmodel", methods=["POST"])
@loginRequired
def trainModelRoute():
    """
    Manual AI model training route.
    """

    try:

        trainingResult = trainTemperatureModel()

        if trainingResult["status"]:

            session["trainingMessage"] = trainingResult["message"]

        else:

            session["trainingMessage"] = trainingResult["message"]

        return redirect("/predict")

    except Exception as error:
        print(f"error | train model route failed | app.py | {error}")

        session["trainingMessage"] = str(error)

        return redirect("/predict")




     
def predictTemperature(afterHours):
    """
    Predict future temperature using trained model.
    """

    try:

        if not os.path.exists(modelPath):

            return {
                "error": "Model not trained yet"
            }

        with open(modelPath, "rb") as modelFile:
            model = pickle.load(modelFile)

        connection = getDbConnection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM logdata
            ORDER BY logid DESC
            LIMIT 1
        """)

        latestLog = cursor.fetchone()

        connection.close()

        if not latestLog:

            return {
                "error": "No sensor data available"
            }

        currentDateTime = datetime.now()

        futureDateTime = currentDateTime.replace(
            hour=(currentDateTime.hour + afterHours) % 24
        )

        predictionInput = np.array([[
            futureDateTime.hour,
            futureDateTime.weekday(),
            float(latestLog["humval"]),
            float(latestLog["soilmoistureval"]),
            int(latestLog["rainval"])
        ]])

        predictedTemperature = model.predict(
            predictionInput
        )[0]

        predictedTemperature = round(
            float(predictedTemperature),
            2
        )

        return {
            "currentTemp": latestLog["tempval"],
            "predictedTemp": predictedTemperature,
            "futureHour": futureDateTime.hour,
            "afterHours": afterHours,
            "humidity": latestLog["humval"],
            "soilMoisture": latestLog["soilmoistureval"],
            "rainValue": latestLog["rainval"]
        }

    except Exception as error:
        print(f"error | predict temperature failed | app.py | {error}")

        return {
            "error": str(error)
        }
     
     
     
     
@app.route("/predict", methods=["GET", "POST"])
@loginRequired
def predictPage():
    """
    Temperature prediction page.
    """

    try:

        predictionData = None
        selectedHours = 1

        trainingMessage = session.pop(
            "trainingMessage",
            None
        )

        if request.method == "POST":

            selectedHours = int(
                request.form.get("hours", 1)
            )

            predictionData = predictTemperature(
                selectedHours
            )

        return render_template(
            "predict.html",
            predictionData=predictionData,
            selectedHours=selectedHours,
            trainingMessage=trainingMessage
        )

    except Exception as error:
        print(f"error | predict page failed | app.py | {error}")
        return "Internal Server Error"     
     



if __name__ == "__main__":

    initDatabase()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )