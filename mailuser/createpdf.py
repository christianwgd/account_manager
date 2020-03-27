# -*- coding: utf-8 -*-
"""The code used to generate PDF files (based on Reportlab)."""

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import utils
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from django.utils.translation import ugettext as _

from . import crypt

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="Footer", alignment=TA_CENTER, fontName="Helvetica-Oblique",
    textColor=colors.lightgrey
))
styles.add(ParagraphStyle(
    name="Warning", fontName="Helvetica-Oblique",
    textColor=colors.red, fontSize=12
))
styles.add(ParagraphStyle(
    name="Link",
    textColor=colors.blue
))
styles.add(ParagraphStyle(
    name="Greeting", alignment=TA_CENTER, fontName="Helvetica-Oblique",
    fontSize=14
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
        canvas.setCreator("MailUser")
        footer = [Paragraph(_("Powered by MailUser"),
                            styles["Footer"])]
        Frame(0, 0, 21 * cm, 2 * cm).addFromList(footer, canvas)

    filename = crypt.get_creds_filename(account)
    buff = BytesIO()
    doc = SimpleDocTemplate(buff, pagesize=A4)
    story = []
    story.append(resized_image(crypt.get_document_logo(account.tenant.logo), 6*cm))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(_("Personal account information"), styles["Title"]))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(_("""
Dear %s, this document contains the credentials you will need
to connect to Modoboa. Learn the content and destroy
the document as soon as possible.
""") % account.full_name, styles["Normal"]))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(_("Web panel:"), styles["h3"]))
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
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5 * cm))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        _("Please change your password!"),
        styles["Warning"]))

    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        _("PC/Tablet/Smartphone configuration:"), styles["h3"]))
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
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        _("Use those settings for your computer, tablet or phone."),
        styles["Normal"])
    )

    # if conf["custom_message"]:
    #     story.append(Spacer(1, 2 * cm))
    #     story.append(Paragraph("custom_message", "Greeting"))

    doc.build(story, onFirstPage=page_template, onLaterPages=page_template)
    length = len(buff.getvalue())
    buff.seek(0)
    crypt.crypt_and_save_to_file(buff, filename, length)