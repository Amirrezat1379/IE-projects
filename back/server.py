import jwt
from fastapi import FastAPI, Request, HTTPException, status
import mysql.connector
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import uvicorn
import requests


scheduler = BackgroundScheduler()
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
  mycursor.execute("CREATE TABLE linkstatus (link VARCHAR(255), status VARCHAR(4))")
  mycursor.execute("CREATE TABLE links (name VARCHAR(255), link VARCHAR(255))")
  mycursor.execute("CREATE TABLE customers (name VARCHAR(255), encodeData VARCHAR(255))")
except:
  print("table exict")

sql = "INSERT INTO customers (name, encodeData) VALUES (%s, %s)"
linkSql = "INSERT INTO links (name, link) VALUES (%s, %s)"
statusSql = "INSERT INTO linkstatus (link, status) VALUES (%s, %s)"

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
linkSql2 = "SELECT link FROM links WHERE name = %s"
statusSql2 = "SELECT status FROM linkstatus WHERE link = %s"
adr = ("Amir", )

mycursor.execute(linkSql, ("Amir", "https://www.google.com"))
mycursor.execute("SELECT link FROM links WHERE name = 'Amir'")

myresult = mycursor.fetchall()
print(myresult)

try:
  jwt.decode("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb21lIjoicGF5bG9hZCJ9.4twFt5NiznN84AWoo1d7KO1T_yoc0Z6XOpOVswacPZg", SECRET_KEY, algorithms="HS256")
except jwt.exceptions.InvalidSignatureError:
  print("Boro khodeto sare kar bezar :))")

# print(requests.get(url = "https://google.com").detail)

def get_status(link):
  print("OK")
  code = requests.get(url = link).status_code
  code = str(code)
  print(code)
  mycursor.execute(statusSql, (link, code))
  mydb.commit()

  print(mycursor.rowcount, "record inserted.")
  
  # print(r)

@app.get("/getStatus")
async def getStatus(request: Request):
  mycursor.execute("SELECT * FROM linkstatus")
  print(mycursor.fetchall())
  res = []
  user = check(request.headers["authorization"])
  try:
    mycursor.execute(linkSql2, (user["username"],))
    myresult = mycursor.fetchall()
    print(myresult)
    for item in myresult:
      print(item[0])
      mycursor.execute(statusSql2, (item[0],))
      myresults = mycursor.fetchall()
      print(myresults)
      for it in myresults:
        res.append(it)
  except:
    return "No Status"
  return res

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
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Wrong Password"
    )

@app.get("/getLinks")
async def getLinks(request: Request):
  user = check(request.headers["authorization"])
  mycursor.execute(linkSql2, (user["username"],))
  return mycursor.fetchall()
  

def check(authorize):
  try:
    user = jwt.decode(authorize, SECRET_KEY, algorithms=["HS256"])
    return user
  except jwt.exceptions.InvalidSignatureError:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
    )

@app.post("/insertLink")
async def insertLink(request: Request):
  inputDict = await request.json()
  user = check(request.headers["authorization"])
  if (user["expire"] >= datetime.now().__str__()):
    mycursor.execute(linkSql2, (user["username"],))
    myresult = mycursor.fetchall()
    print(len(myresult))
    if (len(myresult) <= 20):
      mycursor.execute(linkSql, (user["username"], inputDict["link"]))
    else:
      raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too Many Links"
      )
    print(int(inputDict["time"]))
  else:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Token Expired!!!"
    )
    

if __name__ == "__main__":
    scheduler.add_job(func=get_status, max_instances=5, trigger="interval", seconds=2, args=["https://www.google.com"])
    scheduler.start()
    uvicorn.run(
        app = "server:app",
        host = "0.0.0.0",
        port = 8100,
        reload = True,
    )
  