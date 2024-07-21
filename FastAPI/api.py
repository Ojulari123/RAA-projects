from fastapi import FastAPI, Path
from typing import Optional
from pydantic import BaseModel
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

app = FastAPI()

db = []

class Student_record(Model):
     id = fields.IntField(pk=True)
     name = fields.CharField(50,unique=True)
     age = fields.IntField(50)

students = {
    1: {
        "name": "OJ",
        "age": 17,
        "class": "year 12"
    }
}


student_pydantic = pydantic_model_creator(Student_record, name="student")
student_info = pydantic_model_creator(Student_record, name="Student", exclude_readonly=True)

class Student(BaseModel):
    name: str
    age : int
    year : str

class Update_Student(BaseModel):
    name :  Optional[str] = None
    age : Optional[int] = None
    year : Optional[str] = None

@app.get("/")
def index():
    return {"name" : "First Data"}

@app.get("/get-student/{student_id}")
def get_student(student_id: int = Path(..., description="The ID of the student you want to view", gt=0)):
        return students[student_id]

@app.get("/get-by-name/{student_id}")
def get_student(*, student_id: int, name: Optional[str] = None):
    for student_id in students:
         if students[student_id]["name"] == name:
              return students[student_id]
    return{"Data" : "Not Found"}

@app.post("/create-student/{student_id}")
def create_student(student_id: int, student: Student):
     if student_id in students:
          return {"Error" : "Student Exists"}
     
     students[student_id] = student
     return students[student_id]

@app.put("/update-student/{student_id}")
def update_students(student_id: int, student: Update_Student):
    if student_id not in students:
        return{"Error" : "Student Does Not Exists"}

    if student.name != None:
        students[student_id].name = student.name

    if student.age != None:
        students[student_id].age = student.age

    if student.year != None:
        students[student_id].year = student.year

    return students[student_id]

@app.delete("/delete-student/{student_id}")
def delete_student(student_id: int):
     if student_id not in students:
           return{"Error" : "Student Does Not Exists"}
     del students[student_id]
     return{"Message" : "Student Deleted Successfully"}

# register_tortoise(
#      app,
#      db_url = "sqlite://db.sqlite3"
#      modules={"models":["main"]},
#      generate_schemas=True,

# )
