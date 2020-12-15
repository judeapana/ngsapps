import os
import secrets

from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename


def img_upload(file_storage, resize=(450, 450), base_dir='protected', allowed=None):
    if allowed is None:
        allowed = {'png', 'jpg', 'jpeg', 'gif'}
    filename = secure_filename(file_storage.filename)
    ext = filename.split('.')[-1]
    if not (ext in allowed):
        return {'message': dict(error='file extension not allowed', other='allowed extensions are', extensions=allowed)}
    cur_file_name = f'{secrets.token_hex(20)}.{ext}'
    path = os.path.join(current_app.root_path, 'static', f'{base_dir}/{cur_file_name}')
    ret = {'filename': cur_file_name, 'upload': file_storage, 'full_path': path}
    image = Image.open(file_storage)
    image.thumbnail(resize)
    ret['upload'] = image
    return ret


def delete_file(filename, base_dir='protected'):
    path = os.path.join(current_app.root_path, 'static', f'{base_dir}/{filename}')
    if not os.path.isfile(path):
        return {'message': dict(error='File Not Found')}
    os.remove(path)
    return {'message': dict(success='File removed')}


def file_upload(file_storage, base_dir='protected', allowed=None):
    if allowed is None:
        allowed = {'pdf', 'docx', 'doc', 'zip'}
    filename = secure_filename(file_storage.filename)
    ext = filename.split('.')
    if not (ext[-1] in allowed):
        return {'message': dict(error='file extension not allowed', other='allowed extensions are', extensions=allowed)}
    cur_file_name = f'{"".join(ext[:-1])}_{secrets.token_hex(20)}.{ext[-1]}'
    path = os.path.join(current_app.root_path, 'static', f'{base_dir}/{cur_file_name}')
    ret = {'filename': cur_file_name, 'upload': file_storage, 'full_path': path}
    return ret
