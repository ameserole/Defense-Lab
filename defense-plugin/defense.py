from flask import current_app as app, render_template, request, redirect, url_for, session, Blueprint # NOQA

from CTFd.models import db, Pages, Challenges
from CTFd.utils import authed


def load(app): # NOQA
    defense = Blueprint('defense', __name__, template_folder='defense-templates')
    app.register_blueprint(defense, url_prefix='/defense')
    page = Pages('defense', """ """)
    auth = Blueprint('auth', __name__) # NOQA

    defenseExists = Pages.query.filter_by(route='defense').first()
    if not defenseExists:
        db.session.add(page)
        db.session.commit()

    @app.route('/defense', methods=['GET'])
    def defense_view():
        if not authed():
            return redirect(url_for('auth.login', next=request.path))
        challenge_list = Challenges.query.filter_by(category='Secure Coding/Config').all()
        challenge_names = []
        for challenge in challenge_list:
            challenge_names.append(challenge.name)

        return render_template('defense.html', user=session['id'], challenge_names=challenge_names)
