# falkooxc_tools

These tools were created by Falko
https://openxcom.org/forum/index.php/topic,2980.0.html

They have uploaded the source code as an attachment to the forum
https://openxcom.org/forum/index.php/topic,2980.msg149961.html#msg149961

To preserve the tools I took the liberty to put them on git and run it on my pythonanywhere instance
https://buscher.eu.pythonanywhere.com

## Guide for setting up on eu.pythonanywhere.com

The falko tools are flask apps

To get it to run, try the following
* Register an account @ pythonanywhere.com (free plan is sufficient)
* Go into your dashboard
https://eu.pythonanywhere.com/user/{Your_Name}/
* Click on "Open Web tab"
* Click on "Add a new web app"
* Next
* Click on Flask
* Select latest Python (in this case 3.9)
* Set the path to 
/home/{Your_Name}/mysite/flask_app.py
It's important to keep it at 'mysite' as some inbuilt function will return the path
* Go back to your dashboard and open a bash shell

```
pip3 install --upgrade werkzeug

cd
clone https://github.com/BeatAroundTheBuscher/falkooxc_tools
cp falkooxc_tools/falkooxc2/mysite/* mysite
mv start.py app_flask.py
```
* Go back to your Web tab and click on the Reload Button
* Test your Instance (link is above the Reload Button)