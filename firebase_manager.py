import pyrebase
import requests
import json

def upload_file(firebase_path, local_path, id_token):
    config = {
        'apiKey': 'AIzaSyAQrvuWyhWY5blT26vxbDHl3UfhnN5SNrM',
        'authDomain': 'led-mask.firebaseapp.com',
        'databaseURL': 'https://led-mask.firebaseio.com',
        'storageBucket': 'led-mask.appspot.com'
    }

    firebase = pyrebase.initialize_app(config)

    # auth = firebase.auth()

    # user = auth.sign_in_with_email_and_password('xorms987@gmail.com', 'tktk1234')

    # print('token', user['idToken'])

    storage = firebase.storage()

    storage.child(firebase_path).put(local_path, id_token)

def upload_analysis_document(document, user_uid, id_token):
    response = requests.post(
        url='https://firestore.googleapis.com/v1beta1/projects/led-mask/databases/(default)/documents/users/%s/analysis_histories' % user_uid,
        # auth=('Authorization', 'Bearer %s' % id_token),
        data=json.dumps(document),
        headers={
            # 'Authorization': 'Bearer %s' % id_token,
        'Content-Type': 'application/json'})
    response = json.loads(response.text)
    print('document create response : {}'.format(response))

def upload_therapy_document(document, user_uid, id_token):
    response = requests.post(
        url='https://firestore.googleapis.com/v1beta1/projects/led-mask/databases/(default)/documents/users/%s/therapy_histories' % user_uid,
        # auth=('Authorization', 'Bearer %s' % id_token),
        data=json.dumps(document),
        headers={
            # 'Authorization': 'Bearer %s' % id_token,
            'Content-Type': 'application/json'})
    response = json.loads(response.text)
    print('document create response : {}'.format(response))

def get_user_lists(mask_uid):
    response = requests.get(
        url='https://firestore.googleapis.com/v1beta1/projects/led-mask/databases/(default)/documents/masks/%s' % mask_uid,
        # auth=('Authorization', 'Bearer %s' % id_token),
        headers={
            # 'Authorization': 'Bearer %s' % id_token,
            'Content-Type': 'application/json'})
    response = json.loads(response.text)
    try:
        users_arr = response['fields']['users']['arrayValue']['values']
        user_names_arr = response['fields']['user_names']['arrayValue']['values']
        user_list = []
        for i in range(0, len(users_arr)):
            user_uid = users_arr[i]['referenceValue'].split('/')[-1]
            user_name = user_names_arr[i]['stringValue']
            user_list.append( (user_uid, user_name) )
        return user_list
    except:
        return []

