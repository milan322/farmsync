import os
import json
import uuid
import time
from os.path import join
from farmsync import utility as util
from farmsync import s3_helper, models
from farmsync import config
from farmsync.utility import logger, create_dir, remove_dir


class Comments(object):
    def __init__(self, limit):
        self.limit_recs = limit


    def get_comments(self):
        activitiese_list = models.FSActivity.query.limit(self.limit_recs).all()
        activities_list_json = []
        for activity in activitiese_list:
            response_dict = activity.__dict__
            comments_list = []
            images_list = []
            ratings_list = []
            for comment in activity.comments_info:
                comments_list.append(comment.__dict__)
            for image in activity.images_info:
                images_list.append(image.__dict__)
            for rating in activity.ratings_info:
                ratings_list.append(rating.__dict__)
            response_dict['comments'] = comments_list
            response_dict['images'] = images_list
            response_dict['ratings'] = ratings_list
            activities_list_json.append(response_dict)
        return True, activities_list_json


    def get_dashboard_results(self, user_role, user_name):
        response_dict = {}
        user = models.FSUser.query.filter_by(username=user_name).one()
        if user is None:
            return False, "User " + str(user_name) + " is not registered yet."
        if user_role not in user.user_role:
            return False, "User role is " + str(user_role) + " is not valid."
        comments_recent = models.FSComments.query.filter(commented_by=user.user_id).limit(self.limit_recs).all()
        if comments_recent is None:
            response_dict['comments'] = []
        else:
            comments_list = []
            for comment in comments_recent:
                comments_list.append(comment.__dict__)
            response_dict['comments'] = comments_list

        response_dict['user_profile'] = user.__dict__
        if user_role == 'farmer':
            response_dict['rewards_claim_url'] = 'https://www.bighaat.com/collections/dupont-pioneer'
            pathologists = models.FSUser.query.filter_by(user_role='pathologist').limit(self.limit_recs).all()
            if pathologists is None:
                response_dict['top_pathologist'] = []
            else:
                response_dict['top_pathologist'] = [cuser.__dict__ for cuser in pathologists]
        elif user_role == 'pathologist':
            response_dict['rewards_claim_url'] = 'https://www.amazon.com/'
        else:
            response_dict['rewards_claim_url'] = 'https://www.globoforce.net/store/#!corteva'
        return True, response_dict


    def add_comment(self, user_name, activity_id, comment_header, comment_desc):
        activity = models.FSActivity.query.filter_by(activity_id=activity_id).one()
        if activity is None:
            return False, "Invalid activity id, that activity is not present in database."
        user = models.FSUser.query.filter_by(username=user_name).one()
        if user is None:
            return False, "User " + str(user_name) + " is not registered yet."
        user.user_rewards += 1
        comment_rec = models.FSComments(comment_desc=comment_desc, comment_metadata={'header': comment_header}, commented_time=int(time.time()), commented_by=user.user_id)
        activity.comments_info.append(comment_rec)
        util.add_query(activity)
        util.add_query(user)
        util.commit_query()
        return True, " Added comment successfully."


