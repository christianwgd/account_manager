# -*- coding: utf-8 -*-
"""The code used to generate PDF files (based on Reportlab)."""
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import utils
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab import rl_config

from django.utils.translation import gettext as _
from django.conf import settings

from account import crypt


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="Footer", alignment=TA_CENTER,
    textColor=colors.lightgrey
))
styles.add(ParagraphStyle(
    name="Left", fontSize=12, fontName="IBMPlex", leading=16
))
styles.add(ParagraphStyle(
    name="Tableheader", alignment=TA_CENTER, fontSize=14, fontName="IBMPlex",
))


def resized_image(path, width=1*cm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))


def password_credentials(account):
    """Generate a PDF document containing account credentials."""

    def page_template(canvas, doc):
        canvas.setTitle(_("Personal account information"))
        canvas.setAuthor(account.tenant.name)
        canvas.setCreator("AccountManager")
        canvas.setFont("IBMPlex", 12)  # choose your font type and font size
        footer = [Paragraph(_("Powered by AccountManager"), styles["Footer"])]
        Frame(0, 0, 21 * cm, 2 * cm).addFromList(footer, canvas)

    rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/account/reportlab/font')
    pdfmetrics.registerFont(TTFont('IBMPlex', 'IBMPlexSansCondensed-Regular.ttf'))

    filename = crypt.get_creds_filename(account)
    buff = BytesIO()
    doc = SimpleDocTemplate(buff, pagesize=A4)
    story = []
    story.append(resized_image(crypt.get_document_logo(account.tenant.logo), 6*cm))
    story.append(Paragraph(account.tenant.name, styles["Title"]))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(_("Personal account information"), styles["Title"]))
    story.append(Spacer(1, 1 * cm))
    name = account.name

    story.append(Spacer(1, 1 * cm))
    data = [
        [_("name"), account.name],
        [_("user"), account.user],
        [_("username"), account.username],
        [_("name"), account.full_name],
        [_("description"), account.description],
        [_("password"), account.def_pwd],
        [_("comment"), account.comment],
    ]
    table = Table(data)
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (-1, -1), 'IBMPlex'),
    ]))
    story.append(table)

    doc.build(story, onFirstPage=page_template, onLaterPages=page_template)
    length = len(buff.getvalue())
    buff.seek(0)
    crypt.crypt_and_save_to_file(buff, filename, length)