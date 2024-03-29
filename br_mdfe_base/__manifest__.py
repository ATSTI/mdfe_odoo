# -*- coding: utf-8 -*-
{
    'name': 'Emissor de MDF-e',

    'summary': 'Emissor de MDF-e',

    'description': """
        Esse modulo foi desenvolvido para emissão de Manifesto de 
       forma bem simples e concreta em vista da sefaz.
    """,

    'author': "Implanti Soluções",
    'website': "http://www.implanti.com.br",
    'category': 'Manufacturing',
    'version': '1.0',
    'depends': ['account', 'br_account', 'base'],
    'external_dependencies': {
        'python': [
            'dateutil',
            'mdfelib',
            'erpbrasil.assinatura'
        ]
    },
    'data': [
        'views/views.xml',
        'data/data.xml',
    ],
}
