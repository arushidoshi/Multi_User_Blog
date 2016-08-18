# Multi_User_Blog
submitted by [Arushi Doshi](https://github.com/arushidoshi), for the purpose of completing the third lesson of :
[Full-Stack Web Developer Nanodegree](https://www.udacity.com/course/nd004)

# About This project
* A blogging website where any user can view posts. 
* Registered Users can:
 * edit and delete their posts.
 * Like/Unlike other users' posts. 
 * Users can insert/edit/delete comments on any post.
* It is a fully-responsive website created using HTML, CSS, bootstrap framework, Google App Engine and Google Datastore.

## Package Includes
* templates folder -- _html files for different pages_
* css folder
 * bootstrap.css
 * bootstrap.min.css
* myapp.py -- _python program that manages everything_
* app.yaml -- _contains information about our app_
* index.yaml -- _contains necessary information for database management_

## Usage:
#### To run this project locally, follow these steps:
##### Using GoogleAppEngineLauncher (recommended)
1. Download [GoogleAppEngineLauncher](https://storage.googleapis.com/appengine-sdks/featured/GoogleAppEngineLauncher-1.9.40.dmg)
2. Clone this repository
3. Unzip the contents from the cloned repository
4. Open the GoogleAppEngineLauncher and choose the option "Add an existing application" from the Menu bar and select the unzipped repository
5. Click the "Run" button and navigate to the port mentioned for the app in the GoogleAppEngineLauncher. 
   If this is the first time you're running a Google-App-Engine app you will have the site open at : localhost:8080

##### Using Terminal/Command Line (if you know what you're doing)
1. Download [GoogleAppEngineSDK for python](https://cloud.google.com/appengine/downloads)
2. Clone this repository
3. Unzip the contents from the cloned repository and the SDK
4. Open Terminal and go to the project folder cloned from git
5. Add path to the GoogleAppEngine folder, by typing this command: `export PATH=$PATH:/path_to_folder/google_appengine` where path_to_folder is a path on your computer.
6. Now deploy the application on your localhost:8080 by using the command `dev_appserver.py .`

##### Live version available at: [multiuserblogbyarushi.appspot.com](http://multiuserblogbyarushi.appspot.com/)

# License
The content of this repository is licensed under [MIT License](https://opensource.org/licenses/MIT)
