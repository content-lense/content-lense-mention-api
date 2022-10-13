from flask import Flask, request

import pipeline

from testArticle import article as testArticle

app = Flask(__name__)

@app.route('/articles', methods=['POST'])
def postArticles():
    data = request.json
    res=pipeline.processArticle(data)
    return res

@app.route('/people', methods=['GET'])
def getPeople():
    data = request.args
    if (data['name']):
        return {'data': pipeline.ec.getMostLikelyEntityByName(data['name'])}

@app.route('/articles/example',methods=['GET'])
def getExampleArtilce():
    return testArticle

if __name__ == '__main__':
    app.run(host='0.0.0.0')  # run our Flask app