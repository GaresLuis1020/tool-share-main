from toolshare import app, db
from toolshare.models import AppUser

#Debug mode is set to True, Ensure it's False before deployment
if __name__ == '__main__':
    app.run(debug=True)

# This provides shell context to allow testing: will not be required for deployment 
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'AppUser': AppUser}