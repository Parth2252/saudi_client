{
    'name': "Separate RFQ and PO Sequences",
    'version': '1.0',
    'author': "Your Name",
    'category': 'Purchases',
    'summary': "Use separate sequences for RFQ and PO numbers with last two digits of the year.",
    'depends': ['purchase'],
    'data': [
        'data/ir_sequence_data.xml',
    ],
    'installable': True,
    'application': False,
}
