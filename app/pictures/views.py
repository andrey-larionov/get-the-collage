from flask.views import MethodView
from models import Picture
from flask import jsonify, request, make_response
from instagram import InstagramAPI
import requests
import os
from app import db
import json
from pprint import pprint
from config import UPLOAD_DIR


class PictureAPI(MethodView):

    def _get_instagram_user_id(self, access_token, q):
        api = InstagramAPI(access_token=access_token)

        users = api.user_search(q=q, count=1000)
        uid = None
        for u in users:
            if u.username == q:
                uid = u.id
                break

        if not uid and len(users):
            uid = users[0].id

        return uid

    def _user_popular_media(self, user_id, access_token, count, type='image', limit=5):
        endpoint = "https://api.instagram.com/v1/users/%s/media/recent/" % user_id
        payload = {
            'access_token': access_token,
            'count': count
        }
        r = requests.get(endpoint, payload)

        result = r.json()
        if 'data' not in result:
            return []

        # Sort media by likes
        popular = sorted(result[u'data'], key=lambda k: k[u'likes'][u'count'], reverse=True)

        # Slice popular media by limit and filter by type
        popular_sliced = []
        i = 0
        for item in popular:
            if i >= limit:
                break
            if item[u'type'] != type:
                continue
            popular_sliced.append(item)
            i += 1

        return popular_sliced

    def _download_file(self, url, uid, filename):
        path = '%s/%s/%s' % (UPLOAD_DIR, uid, filename)
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            with open(path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)

    def _store_media(self, media):
        stored = []
        for item in media:
            url = item['images']['standard_resolution']['url']
            filename = url.rsplit('/', 1)[-1]
            uid = item['user']['id']

            stored.append({
                "uid": uid,
                "filename": 'uploads/%s/%s' % (uid, filename),
                "src": item['images']['standard_resolution']['url']
            })
            self._download_file(url, uid, filename)

            if Picture.query.filter_by(uid=uid, name=filename).first():
                continue
            db.session.add(Picture(uid=uid, name=filename))
        db.session.commit()
        return stored

    def get(self):
        pictures = Picture.query.all()

        return jsonify(pictures=[p.serialize() for p in pictures])

    def post(self):

        if not request.json:
            error = json.dumps({"error": "Data should be json encoded"})
            return make_response(error, 400)
        if 'access_token' not in request.json:
            error = json.dumps({"error": "access_token is required"})
            return make_response(error, 403)
        if 'q' not in request.json or not request.json['q']:
            error = json.dumps({"error": "q is required"})
            return make_response(error, 400)

        access_token = request.json['access_token']
        q = request.json['q']

        uid = self._get_instagram_user_id(access_token, q)
        if not uid:
            error = json.dumps({"error": "User not found"})
            return make_response(error, 404)

        media = self._user_popular_media(user_id=uid, access_token=access_token, count=1000)
        media = self._store_media(media)
        pprint(media)
        return jsonify(data=media)