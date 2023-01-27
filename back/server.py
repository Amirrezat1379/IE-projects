import jwt
from fastapi import FastAPI, Request, HTTPException, status
import mysql.connector
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
import uvicorn
from typing import Union
import requests

app = FastAPI()
SECRET_KEY = "09d25e094faa****************f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

# mydb = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   password="54Peim@n"
# )

dataBase = "IEProject"
# myInput = input("make schema?! ")

# # preparing a cursor object
# mycursor = mydb.cursor()

# if (myInput == "y"):
  
#   dataBase = input("Enter schema name: ")

#   # creating database
#   mycursor.execute("CREATE DATABASE IEProject")

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="54Peim@n",
  database = dataBase
)

mycursor = mydb.cursor()
# mycursor.execute("DROP TABLE customers")
try:
  mycursor.execute("CREATE TABLE customers (name VARCHAR(255), encodeData VARCHAR(255))")
  mycursor.execute("CREATE TABLE links (name VARCHAR(255), link VARCHAR(255))")
except:
  print("table exict")

sql = "INSERT INTO customers (name, encodeData) VALUES (%s, %s)"

mycursor.execute(sql, ("Amir", "khar"))

# encoded_jwt = jwt.encode({"username": "Amirreza", "password": "54peiman"}, "secret", algorithm="HS256")

# mycursor.execute(sql, ("Amirreza", encoded_jwt))
# mydb.commit()

# print(mycursor.rowcount, "record inserted.")
string = "Amir"
# mycursor.execute("SELECT * FROM customers")
# mycursor.execute(f"SELECT * FROM customers WHERE name = {string}")

# myresult = mycursor.fetchall()

# print(myresult)
sql2 = "SELECT encodeData FROM customers WHERE name = %s"
adr = ("Amir", )

mycursor.execute(sql2, adr)

myresult = mycursor.fetchall()
print(myresult[0][0])

try:
  jwt.decode("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb21lIjoicGF5bG9hZCJ9.4twFt5NiznN84AWoo1d7KO1T_yoc0Z6XOpOVswacPZg", SECRET_KEY, algorithms="HS256")
except jwt.exceptions.InvalidSignatureError:
  print("Boro khodeto sare kar bezar :))")

# print(requests.get(url = "https://google.com").status_code)

def get_status(link, username):
  r = requests.get(url = link)
  print(r)

scheduler = BlockingScheduler()

@app.post("/addUser")
async def addUser(request: Request):
  inputDict = await request.json()
  # print(inputDict)
  encoded_jwt = jwt.encode(inputDict, SECRET_KEY, algorithm="HS256")
  mycursor.execute(sql, (inputDict["username"], encoded_jwt))

@app.get("/getToken")
async def getToken(request: Request):
  inputDict = await request.json()
  mycursor.execute(sql2, (inputDict["username"],))
  myresult = mycursor.fetchall()
  hashedData = myresult[0][0]
  password = jwt.decode(hashedData, SECRET_KEY, algorithms=["HS256"])
  password = password["password"]
  if password == inputDict["password"]:
    expire = datetime.now() + timedelta(minutes=30)
    inputDict.update({"expire": expire.__str__()})
    encoded_jwt = jwt.encode(inputDict, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
  else:
    return "Invalid Password"

@app.post("/insertLink")
async def insertLink(request: Request):
  inputDict = await request.json()
  try:
    user = jwt.decode(request.headers["authorization"], SECRET_KEY, algorithms="HS256")
  except jwt.exceptions.InvalidSignatureError:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
    )
  if (user["expire"] >= datetime.now()):
    scheduler.add_job(func=get_status, max_instances=5, trigger="interval", minutes=inputDict["time"], args=[inputDict["link"], user["username"]])
  else:
    return "Token Expired"
    

if __name__ == "__main__":
    uvicorn.run(
        app = "server:app",
        host = "0.0.0.0",
        port = 8800,
        reload = True,
    )
  