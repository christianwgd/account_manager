"""Internal library."""

from __future__ import unicode_literals

from io import BytesIO
import os
import struct

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from django.conf import settings
from django.utils.encoding import force_bytes, smart_bytes
from django.utils.translation import ugettext as _


def init_storage_dir():
    """Create the directory whare documents will be stored."""
    storage_dir = getattr(settings, "STORAGE_DIR", 'media/credentials/')
    if os.path.exists(storage_dir):
        return
    try:
        os.mkdir(storage_dir)
    except (OSError, IOError) as inst:
        raise FileNotFoundError(
            _("Failed to create the directory that will contain "
              "PDF documents (%s)") % inst
        )


def get_creds_filename(account):
    """Return the full path of a document."""
    base_dir = getattr(settings, "BASE_DIR", None)
    storage_dir = getattr(settings, "STORAGE_DIR", 'media/credentials/')
    print(os.path.join(base_dir, storage_dir, account.username + ".pdf"))
    return os.path.join(base_dir, storage_dir, account.username + ".pdf")


def delete_credentials(account):
    """Try to delete a local file."""
    fname = get_creds_filename(account)
    if not os.path.exists(fname):
        return
    os.remove(fname)


def _get_cipher(iv):
    """Return ready-to-user Cipher."""
    key = smart_bytes(settings.SECRET_KEY[:32])
    backend = default_backend()
    return Cipher(
        algorithms.AES(force_bytes(key)),
        modes.CBC(iv),
        backend=backend
    )


def crypt_and_save_to_file(content, filename, length, chunksize=64*512):
    """Crypt content and save it to a file."""
    iv = os.urandom(16)
    cipher = _get_cipher(iv)
    encryptor = cipher.encryptor()
    with open(filename, "wb") as fp:
        fp.write(struct.pack(b"<Q", length))
        fp.write(iv)
        while True:
            chunk = content.read(chunksize)
            if not len(chunk):
                break
            elif len(chunk) % 16:
                chunk += b" " * (16 - len(chunk) % 16)
            fp.write(encryptor.update(force_bytes(chunk)))
        fp.write(encryptor.finalize())


def decrypt_file(filename, chunksize=24*1024):
    """Decrypt the content of a file and return it."""
    buff = BytesIO()
    with open(filename, "rb") as fp:
        origsize = struct.unpack(b"<Q", fp.read(struct.calcsize(b"Q")))[0]
        iv = fp.read(16)
        cipher = _get_cipher(iv)
        decryptor = cipher.decryptor()
        while True:
            chunk = fp.read(chunksize)
            if not len(chunk):
                break
            buff.write(decryptor.update(chunk))
        buff.write(decryptor.finalize())
        buff.truncate(origsize)
    return buff.getvalue()


def get_document_logo(logo):
    """Retrieve path to logo."""
    try:
        logo = os.path.join(settings.MEDIA_ROOT, logo.path)
    except AttributeError:
        logo = None
    return logo