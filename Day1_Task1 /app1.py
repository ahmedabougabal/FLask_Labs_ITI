from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
students = [{"id":1, "name":"Ahmed"}, {"id":2, "name":"Mohamed"}, {"id":3, "name":"Youssef"}]

@app.route('/')
def home_page():
    # return 'Hello, World!'
    return render_template("index.html", students_data=students)



@app.route("/search/<int:id>") # search/1 => data in table of user that has id=1
def search_student(id):
    student_found = False
    searched_student = None
    for student in students:
        if student['id'] == id:
            student_found = True
            searched_student = student
            break
    return render_template("search.html", student_found= student_found, searched_student= searched_student)





if __name__ == '__main__':
    app.run(debug=True,port=5000)