from __main__ import db,UserProfile, Exercise,ExerciseProfile


def db_init():
    db.create_all()

    # db.session.add(ExerciseProfile(username='john', password='P@55word'))
    # db.session.add(ExerciseProfile(username='tom', password='wordP@55'))
    # db.session.add(Exercise(client='john', title='Jumping Jacks', reps=25))
    # db.session.add(Exercise(client='john', title='Jogging', reps=30))
    # db.session.add(Exercise(client='tom', title='Push Ups', reps=10))
    # db.session.add(Exercise(client='tom', title='Lunges', reps=10))

    db.session.commit()