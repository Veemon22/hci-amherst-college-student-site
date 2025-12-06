# hci-amherst-college-student-site
This is a semester long project for my Human-Computer Interaction project. It is a website similar to the Amherst College Mammoth Mobile App. 


To test out my site, clone the repository. Then install all the packages in requirements.txt and setup .env file at the root of the project.

Your .env file should include:
- GOOGLE_CREDENTIALS
- GOOGLE_REDIRECT_URI
- FERNET_KEY
- ADMIN_USERNAME
- FLASK_SECRET_KEY

## IMPORTANT
The google credentials and google_redirect_uri comes from making a google cloud project. You need to make one and include the Google Calendar API. The ferent key comes from the Fernet Library which you can use to make that KEY. 

After setting all that up, run flask --app main run within the virtual enviornment.

