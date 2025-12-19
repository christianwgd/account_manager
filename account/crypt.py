"""Internal library."""
from io import BytesIO
import os
import struct
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from django.conf import settings
from django.utils.encoding import force_bytes, smart_bytes
from django.utils.translation import gettext as _


def init_storage_dir():
    """Create the directory whare documents will be stored."""
    storage_dir = getattr(settings, "STORAGE_DIR", 'media/credentials/')
    if Path(storage_dir).exists():
        return
    try:
        Path(storage_dir).mkdir()
    except OSError as inst:
        raise FileNotFoundError(
            _("Failed to create the directory that will contain "
              "PDF documents (%s)") % inst
        ) from inst


def get_creds_filename(account):
    """Return the full path of a document."""
    base_dir = getattr(settings, "BASE_DIR", None)
    storage_dir = getattr(settings, "STORAGE_DIR", 'media/credentials/')
    name = account.username if account.type == '1' else f'{account.name}_{account.tenant.name}'
    return Path(base_dir) / storage_dir / f"{name}.pdf"


def delete_credentials(account):
    """Try to delete a local file."""
    fname = get_creds_filename(account)
    if not Path(fname).exists():
        return
    Path.unlink(fname)


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
    with Path.open(filename, "wb") as fp:
        fp.write(struct.pack(b"<Q", length))
        fp.write(iv)
        while True:
            chunk = content.read(chunksize)
            if not len(chunk):
                break
            if len(chunk) % 16:
                chunk += b" " * (16 - len(chunk) % 16)
            fp.write(encryptor.update(force_bytes(chunk)))
        fp.write(encryptor.finalize())


def decrypt_file(filename, chunksize=24*1024):
    """Decrypt the content of a file and return it."""
    buff = BytesIO()
    try:
        with Path.open(filename, "rb") as fp:
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
    except:
        raise


def get_document_logo(logo):
    """Retrieve path to logo."""
    try:
        logo = Path(settings.MEDIA_ROOT) / logo.path
    except AttributeError:
        logo = None
    return logo
