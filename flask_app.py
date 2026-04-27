from flask import Flask , render_template , request
import subprocess

app = Flask(__name__)

@app.route("/" , methods = ["GET" , "POST"])
def index():
    output = "" 
    error =  ""

    if request.method == "POST":
        repo_url = request.form.get("repo")
        task = request.form.get("task")

        if repo_url and task:
            try:
                process = subprocess.Popen(
                    ["python" , "app.py"],
                    stdin = subprocess.PIPE ,
                    stdout = subprocess.PIPE , 
                    stderr = subprocess.PIPE , 
                    text = True
                )

                inputs = f"{repo_url}\n{task}\n"
                output, error = process.communicate(input=inputs)
            except Exception as e:
                error = str(e)
    return render_template("index.html", output=output, error=error)

if __name__== "__main__":
    app.run(debug=True)