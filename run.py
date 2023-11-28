
""" Use this file to run the server for development.
        wdir :
             cd small-auth-app
    
    In production, use `gunicorn` 
    1. using application factory and blueprints
        gunicorn looks for the 
        create_app() func in __init__ of src folder.
        inside this function all blueprints are registered, config etc added
        run with : [BEING USED]
            .venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 "src:create_app()" 

    2. create the app in a app.py file, add whatever additional routes or sth
            .venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 "src.app:app" 
    """


from src import create_app
app = create_app() 


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0',port=8000,debug=True)
    # app.run(debug=True)

