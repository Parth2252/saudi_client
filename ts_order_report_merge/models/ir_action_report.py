import base64
import io
import logging

import lxml.html
from PIL import ImageFile
from PyPDF2 import PdfFileReader, PdfFileWriter

from odoo import fields, models

ImageFile.LOAD_TRUNCATED_IMAGES = True

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def join_pdf(self, pdf_chunks):
        result_pdf = PdfFileWriter()

        for chunk in pdf_chunks:
            chunk_pdf = PdfFileReader(
                stream=io.BytesIO(initial_bytes=chunk)
            )
            for page in range(chunk_pdf.getNumPages()):
                result_pdf.addPage(chunk_pdf.getPage(page))

        response_bytes_stream = io.BytesIO()
        result_pdf.write(response_bytes_stream)
        return response_bytes_stream.getvalue()

    def _run_wkhtmltopdf(
            self,
            bodies,
            report_ref=False,
            header=None,
            footer=None,
            landscape=False,
            specific_paperformat_args=None,
            set_viewport_size=False,
    ):
        res = super()._run_wkhtmltopdf(
            bodies,
            report_ref,
            header,
            footer,
            landscape,
            specific_paperformat_args,
            set_viewport_size,
        )

        report_sudo = self._get_report(report_ref)
        model = report_sudo.model

        doc_ids = specific_paperformat_args.get('ids') if specific_paperformat_args else None
        if not doc_ids or len(doc_ids) != 1:
            return res

        # ✅ For sale.order report
        if model == 'sale.order' and report_ref == 'sale_extension.report_technical_offer':
            sale_order = self.env['sale.order'].browse(doc_ids[0])
            for line in sale_order.order_line:
                if line.datasheet_attach:
                    product = line.offered_description_id or line.product_id
                    if product and product.product_document_ids:
                        for attachment in product.product_document_ids:
                            if attachment.mimetype == "application/pdf":
                                res = self.join_pdf([res, base64.b64decode(attachment.datas)])


        # ✅ For stock.picking report
        elif model == 'stock.picking' and report_ref == 'sale_extension.report_sticker_and_label_document':
            picking = self.env['stock.picking'].browse(doc_ids[0])
            for move in picking.move_ids_without_package:
                if move.datasheet_attach:
                    if move.product_id and move.product_id.product_document_ids:
                        for attachment in move.product_id.product_document_ids:
                            if attachment.mimetype == "application/pdf":
                                res = self.join_pdf([res, base64.b64decode(attachment.datas)])

        return res

    def _prepare_html(self, html, report_model):
        language = self.env.user.lang or "en_US"
        root = lxml.html.fromstring(html)
        match_class = (
            "//div[contains(concat(' ', normalize-space(@class), ' '), ' {} ')]"
        )
        for node in root.xpath(match_class.format("article")):
            if node.get("data-oe-lang"):
                language = node.get("data-oe-lang")
        bodies, res_ids, header, footer, specific_paperformat_args = super(
            IrActionsReport, self
        )._prepare_html(html, report_model)
        specific_paperformat_args.update({"partner_lang": language, "ids": res_ids})
        return bodies, res_ids, header, footer, specific_paperformat_args
