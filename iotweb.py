from flask import Flask,request,url_for,redirect
from iot import DryingRack

app = Flask(__name__,static_folder='h5')
dr = DryingRack()


@app.route('/',methods=['GET','POST'])
def home():
    return redirect('/h5/iot.html')

@app.route("/getstatus",methods=['GET'])
def get_status():
    return dr.get_status()
   

@app.route("/action",methods=['GET',"POST"])
def action():
    if request.method == "POST":
        action = request.form["action"]
    if request.method == "GET":
        action = request.args.get("action","stop")
    print "do "+ action 
    return dr.do_action(action)

@app.route("/config",methods=['GET',"POST"])
def config():
    if request.method == "POST":
        auto_string = request.form["auto"]
    if request.method == "GET":
        auto_string = request.args.get("auto","True")
    print "config: auto= "+ auto_string
    if auto_string in ("True" ,"true","TRUE"):
        auto=True
    else:
        auto=False

    return dr.config({"auto":auto})       


if __name__ == '__main__':
    
    app.run(host="0.0.0.0",port=5000)