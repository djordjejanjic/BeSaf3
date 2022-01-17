from flask import Flask, render_template, request
from flask.helpers import url_for
from flask.wrappers import Response
from werkzeug.utils import redirect
from controller.controller import Controller
from main import Main

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/results')
def results():
    myCursor = Controller.getAll()

    resultValue = myCursor.execute("SELECT * FROM results ORDER BY date DESC")
    if resultValue > 0:
        resultDetails = myCursor.fetchall()
        return render_template('results.html', resultDetails=resultDetails)


@app.route('/results-sorted')
def resultsSorted():
    myCursor = Controller.getAll()
    resultValue = myCursor.execute("SELECT * FROM results ORDER BY result DESC")
    if resultValue > 0:
        resultDetails = myCursor.fetchall()
        return render_template('results-sorted.html', resultDetails=resultDetails)


def gen():
    return Main.startVideo()


@app.route('/delete/<string:id>', methods=['POST', 'GET'])
def deleteResult(id):
    Controller.delete(id)
    return redirect(url_for('results'))


@app.route('/video', methods=['GET', 'POST'])
def video():
    if request.method == 'POST':
        Main.stopAndSave()
        print("IT STOPPED AND SAVED")

    return render_template('video.html')


@app.route('/videofeed')
def videofeed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
