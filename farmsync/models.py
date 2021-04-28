import enum
from farmsync.utility import fs_db
from sqlalchemy.orm import relationship


class FSUser(fs_db.Model):
    __tablename__ = 'fs_user'

    user_id = fs_db.Column(fs_db.Integer, primary_key=True)
    username = fs_db.Column(fs_db.String(50))
    user_email = fs_db.Column(fs_db.String(100))
    user_password = fs_db.Column(fs_db.String(100))
    user_role = fs_db.Column(fs_db.String(100))
    user_uuid = fs_db.Column(fs_db.String(36), nullable=False, unique=True)
    user_rewards = fs_db.Column(fs_db.Integer, default=0)
    rating_summary = fs_db.Column(fs_db.Float, default=5)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<username {}, user_uuid {} user_email {} user_role {}>' \
                .format(self.username, self.user_uuid, self.user_email, self.user_role)

    def as_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'user_email': self.user_email,
            'user_uuid': self.user_uuid,
            'role': self.user_role,
            'reward_points': self.user_rewards,
            'rating_summary': self.rating_summary
        }


class FSActivity(fs_db.Model):
    __tablename__ = 'fs_activity'

    activity_id = fs_db.Column(fs_db.Integer, primary_key=True)
    activity_start_time = fs_db.Column(fs_db.Integer)
    activity_update_time = fs_db.Column(fs_db.Integer)

    comments_info = relationship("FSComments")
    images_info = relationship("FSImages")
    ratings_info = relationship("FSFeedback")

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<username {}, user_uuid {} user_email {} user_role {}>' \
                .format(self.username, self.user_uuid, self.user_email, self.user_role)

    def as_dict(self):
        return {
            'activity_id': self.activity_id,
            'activity_start_time': self.activity_start_time,
            'activity_update_time': self.activity_update_time
        }


class FSComments(fs_db.Model):
    __tablename__ = 'fs_comments'

    comment_id = fs_db.Column(fs_db.Integer, primary_key=True)
    comment_desc = fs_db.Column(fs_db.String(250))
    comment_metadata = fs_db.Column(fs_db.Text) # {'disease': '', 'plant_type': '', 'bacteria': '', 'recommendation': '', ...}
    commented_time = fs_db.Column(fs_db.Integer)
    user_rewards = fs_db.Column(fs_db.Integer, default=0)
    rating_summary = fs_db.Column(fs_db.Float, default=5)

    commented_by = fs_db.Column(fs_db.Integer, fs_db.ForeignKey("fs_user.user_id"), nullable=False)
    commented_activity = fs_db.Column(fs_db.Integer, fs_db.ForeignKey("fs_activity.activity_id"), nullable=False)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class FSImages(fs_db.Model):
    __tablename__ = 'fs_images'

    image_id = fs_db.Column(fs_db.Integer, primary_key=True)
    image_desc = fs_db.Column(fs_db.String(250))
    image_url = fs_db.Column(fs_db.String(500))  #Image S3 url
    image_metadata = fs_db.Column(fs_db.Text) # {'image_cat': 'plant', 'image_feedback': '5'...}

    image_upload_by = fs_db.Column(fs_db.Integer, fs_db.ForeignKey("fs_user.user_id"), nullable=False)
    image_activity = fs_db.Column(fs_db.Integer, fs_db.ForeignKey("fs_activity.activity_id"), nullable=False)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class FSFeedback(fs_db.Model):
    __tablename__ = 'fs_feedback'

    feedback_id = fs_db.Column(fs_db.Integer, primary_key=True)
    feedback_desc = fs_db.Column(fs_db.String(250))
    feedback_rating = fs_db.Column(fs_db.Integer)
    comment_metadata = fs_db.Column(fs_db.Text) # {'disease': '', 'plant_type': '', 'bacteria': '', 'recommendation': '', ...}

    feedback_by = fs_db.Column(fs_db.Integer, fs_db.ForeignKey("fs_user.user_id"), nullable=False)
    feedback_to = fs_db.Column(fs_db.Integer, fs_db.ForeignKey("fs_user.user_id"), nullable=False)
    feedback_activity = fs_db.Column(fs_db.Integer, fs_db.ForeignKey("fs_activity.activity_id"), nullable=False)
    feedback_comment = fs_db.Column(fs_db.Integer, fs_db.ForeignKey("fs_comments.comment_id"), nullable=False)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
