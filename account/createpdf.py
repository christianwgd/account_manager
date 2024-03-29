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
    name="Warning", textColor=colors.red, fontSize=12, fontName="IBMPlex",
))
styles.add(ParagraphStyle(
    name="Link", textColor=colors.blue, fontName="IBMPlex",
))
styles.add(ParagraphStyle(
    name="Left", fontSize=12, fontName="IBMPlex", leading=16
))
styles.add(ParagraphStyle(
    name="Tableheader", alignment=TA_CENTER, fontSize=12, fontName="IBMPlex",
))


def resized_image(path, width=1*cm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))


def credentials(account):
    """Generate a PDF document containing account credentials."""

    def page_template(canvas, doc):
        canvas.setTitle(_("Personal account information"))
        canvas.setAuthor(account.full_name)
        canvas.setCreator("AccountManager")
        canvas.setFont("IBMPlex", 12)  # choose your font type and font size
        footer = [Paragraph(_("Powered by AccountManager"),
                            styles["Footer"])]
        Frame(0, 0, 21 * cm, 2 * cm).addFromList(footer, canvas)

    rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/account/reportlab/font')
    pdfmetrics.registerFont(TTFont('IBMPlex', 'IBMPlexSansCondensed-Regular.ttf'))

    filename = crypt.get_creds_filename(account)
    buff = BytesIO()
    doc = SimpleDocTemplate(buff, pagesize=A4)
    story = []
    story.append(resized_image(crypt.get_document_logo(account.tenant.logo), 6*cm))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(_("Personal account information"), styles["Title"]))
    story.append(Spacer(1, 1 * cm))
    if account.full_name:
        name = account.full_name
    else:
        name = account.username.split('@')[0]
    story.append(Paragraph(_("""
Dear %s, this document contains the credentials you will need
to connect to your email account. Learn the content and destroy
the document as soon as possible.
""") % name, styles["Left"]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(_("Web panel:"), styles["Tableheader"]))
    story.append(Spacer(1, 0.2 * cm))
    data = [
        [_("URL"), account.tenant.weburl],
        [_("username"), str(account.username)],
        [_("password"), account.def_pwd]
    ]
    table = Table(data)
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (1, 0), (1, 0), colors.blue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, -1), 'IBMPlex'),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5 * cm))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        _("Please change your password!"),
        styles["Warning"]))

    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        _("PC/Tablet/Smartphone configuration:"), styles["Tableheader"]))
    story.append(Spacer(1, 0.2 * cm))
    data = [
        [_("manual url"), account.tenant.man_url],
        [_("IMAP server address (Incoming mail server)"), account.tenant.imap_url],
        [_("IMAP server port"), account.tenant.imap_port],
        [_("IMAP connection security"), account.tenant.get_imap_sec_display()],
        [_("SMTP server address (Outgoing mail server)"), account.tenant.smtp_url],
        [_("SMTP server port"), account.tenant.smtp_port],
        [_("SMTP connection security"), account.tenant.get_smtp_sec_display()],
    ]
    table = Table(data)
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (1, 0), (1, 0), colors.blue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, -1), 'IBMPlex'),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        _("Use those settings for your computer, tablet or phone."),
        styles["Left"])
    )

    # if conf["custom_message"]:
    #     story.append(Spacer(1, 2 * cm))
    #     story.append(Paragraph("custom_message", "Greeting"))

    doc.build(story, onFirstPage=page_template, onLaterPages=page_template)
    length = len(buff.getvalue())
    buff.seek(0)
    crypt.crypt_and_save_to_file(buff, filename, length)