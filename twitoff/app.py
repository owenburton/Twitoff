"""Main application and routing logic for Twitoff."""
# This file should only have application configuration and 
# routing logic

# standard order for imports is alphabetical
from decouple import config
from flask import Flask, render_template, request
from .models import DB, User
from .twitter import add_or_update_user
from .predict import predict_user

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template(
            'base.html', 
            title='Home',
            users=users)
    
    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None):
        message = ''
        # import pdb; pdb.set_trace()
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = f'User {name} successfully added!'
            tweets = User.query.filter(User.name == name).one().tweets
        except Exception as e:
            message = f'Error adding {name}: {e}'
            tweets = []
        return render_template(
            'user.html', 
            title=name, 
            tweets=tweets,
            message=message)

    # @app.route('/reset')
    # def reset():
    #     DB.drop_all()
    #     DB.create_all()
    #     return render_template(
    #         'base.html', 
    #         title='DB Reset!',
    #         users=[])

# This decorater routes to the comparison page, and the method compares their tweets
    @app.route('/compare', methods=['POST'])
    def compare(message=''):
        user1 = request.values['user1']
        user2 = request.values['user2']
        tweet_text = request.values['tweet_text']

        if user1 == user2:
            message = 'Cannot compare a user to themselves!'
        else:
            prediction = predict_user(user1, user2, tweet_text)
            message = f'''
                {tweet_text} 
                is more likely to be said by 
                {prediction} than {user1 if prediction else user2}
                '''
        return render_template('prediction.html', title='Prediction', message=message)

# This decorater updates the current crop of tweets for all users, routes to home.html
    @app.route('/update')
    def update():
        update_all_users()
        pass
        return render_template('home.html', users=User.query.all(), title='All Tweets updated!')
    
    return app