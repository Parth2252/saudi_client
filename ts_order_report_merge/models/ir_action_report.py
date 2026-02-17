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
        if not pdf_chunks:
            return b''
        if len(pdf_chunks) == 1:
            return pdf_chunks[0]

        result_pdf = PdfFileWriter()

        for chunk in pdf_chunks:
            try:
                chunk_pdf = PdfFileReader(
                    stream=io.BytesIO(initial_bytes=chunk),
                    strict=False
                )
                for page in range(chunk_pdf.getNumPages()):
                    result_pdf.addPage(chunk_pdf.getPage(page))
            except Exception as e:
                _logger.error("Failed to process PDF chunk for merging: %s", e)
                continue

        response_bytes_stream = io.BytesIO()
        result_pdf.write(response_bytes_stream)
        return response_bytes_stream.getvalue()

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        report_sudo = self._get_report(report_ref)
        
        # Target the specific Technical Offer report
        if report_sudo.report_name == 'sale_extension.report_technical_offer' and res_ids and len(res_ids) == 1:
            # Check if this is a recursive call for a specific part
            if self.env.context.get('rendering_part'):
                return super()._render_qweb_pdf(report_ref, res_ids, data)

            sale_order = self.env['sale.order'].browse(res_ids[0])
            pdfs_to_join = []

            # 1. MAIN REPORT (Summary, Terms, Totals)
            main_pdf, _ = self.with_context(rendering_part=True, render_part='main')._render_qweb_pdf(report_ref, res_ids, data)
            if main_pdf:
                pdfs_to_join.append(main_pdf)

            # 2. INTERLEAVED APPENDIX (Header -> PDF/Image)
            for line in sale_order.order_line:
                if not line.datasheet_attach:
                    continue
                
                # A. Render Header + Image (Single chunk if possible)
                # We render this part even if it's just a header and a note about a PDF
                item_appendix_pdf, _ = self.with_context(
                    rendering_part=True, 
                    render_part='appendix_item', 
                    line_id=line.id
                )._render_qweb_pdf(report_ref, res_ids, data)
                
                if item_appendix_pdf:
                    pdfs_to_join.append(item_appendix_pdf)

                # B. Insert PDF Attachment(s)
                # These will appear immediately after the item's header/image
                
                # Check line upload
                if line.upload_datasheet_attachment and line.is_attachment_pdf():
                    try:
                        pdfs_to_join.append(base64.b64decode(line.upload_datasheet_attachment))
                    except:
                        pass

                # Check product documents
                product = line.offered_description_id or line.product_id
                if product and hasattr(product, 'product_document_ids'):
                    for attachment in product.product_document_ids:
                        if attachment.mimetype == "application/pdf" and attachment.datas:
                            try:
                                pdfs_to_join.append(base64.b64decode(attachment.datas))
                            except:
                                pass

            if pdfs_to_join:
                return self.join_pdf(pdfs_to_join), 'pdf'

        return super()._render_qweb_pdf(report_ref, res_ids, data)

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

        # ✅ For stock.picking report
        if model == 'stock.picking' and report_ref == 'sale_extension.report_sticker_and_label_document':
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
