import os
import json
import uuid
import time
from os.path import join
from farmsync import utility as util
from farmsync import s3_helper, models
from farmsync import config
from farmsync.utility import logger, create_dir, remove_dir

"""
params: {'user': 'xyz', 'email': 'xyz@gmail.com', 'phone': '98xxxxxxxx',  'images': ['1.jpg', '2.png']}
"""
class Image(object):
    def __init__(self, params={}):
        self.user = params.get('username')
        self.email = params.get('email')
        #self.s3_user_dir = "{}-{}".format(self.email, str(uuid.uuid4()))
        self.phone = params.get('phone')
        self.images = params.get('images', [])
        self.user_uuid = params.get('user_uuid')
        self.user_role = params.get('user_role')
        self.subject = params.get('subject')
        self.comment_desc = params.get('comment_desc')
        self.other_desc = params.get('other_desc')
        self.s3_user_dir = "{}/{}-{}".format(config.S3_IMAGE_DIR, self.user, self.user_uuid)

    def get_users(self):
        return self.list_users_from_s3(self)

    def get_user_images(self, user_dir):
        self.s3_user_dir = f"{config.S3_IMAGE_DIR}/{user_dir}"
        user_img_records = s3_helper.get_s3_files(config.S3_BUCKET, self.s3_user_dir)
        return user_img_records

    def insert_activity_record(self, imagepath):
        current_time = int(time.time())
        activity_rec = models.FSActivity(activity_start_time=current_time, activity_update_time=current_time)
        user = models.FSUser.query.filter_by(username=self.user).one()
        if user is not None:
            comment_rec = models.FSComments(comment_desc=self.comment_desc, commented_time=int(time.time()), comment_metadata=self.other_desc, commented_by=user.username)
            image_rec = models.FSImages(image_url=imagepath, image_upload_by=user.user_id)
            activity_rec.comments_info.append(comment_rec)
            activity_rec.images_info.append(image_rec)
            if not user.user_rewards:
                user.user_rewards = 0
            user.user_rewards += 20
            util.add_query(activity_rec)
            util.add_query(user)
            util.commit_query()
            return True, ""
        else:
            return False, "User is not found " + self.user

    def upload_image_to_s3(self):
        user_dir = f"{self.user}-{self.user_uuid}"
        temp_user_dir = f"{config.TEMP_DIR}/{user_dir}"
        create_dir(temp_user_dir)
        for file_obj in self.images:
            temp_fpath = f"{temp_user_dir}/{file_obj.filename}"
            file_obj.save(temp_fpath)
            if self.is_crop_image(temp_fpath):
                dest_fpath = f"{self.s3_user_dir}/{file_obj.filename}"
                s3_helper.upload_file_to_s3(config.S3_BUCKET, temp_fpath, dest_fpath)
                status , status_msg = self.insert_activity_record(self.s3_user_dir+ '/' + file_obj.filename)
                if status is False:
                    return status, status_msg
        remove_dir(temp_user_dir)
        return True, ""

    def is_crop_image(self, image):
        is_crop = False
        object_types = ['plant', 'agriculture', 'field']
        crop_types = [
                        'rice', 'maize', 'paddy', 'wheat', 'cotton', 'soybeans', \
                        'corn', 'barley', 'groundnuts', 'apples', 'bananas', 'tomato', \
                        'potato', 'carrot', 'sugarcanes', 'pumpkin'
                     ]

        #confidence_thresh = 98.0
        for label in s3_helper.detect_image_labels(image):
            name = label.get('Name')
            #confidence = label.get('Confidence')
            if name.lower() in object_types or \
                name.lower() in crop_types: # and confidence >= confidence_thresh:
                is_crop = True
                break
        return is_crop

    @staticmethod
    def list_users_from_s3(self):
        try:
            users = s3_helper.list_s3_objects(config.S3_BUCKET, config.S3_IMAGE_DIR)
            return users
        except Exception as e:
            logger.error('Failed to get Users from S3 with error: {}'.format(str(e)))
            raise