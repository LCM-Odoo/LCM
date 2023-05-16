{
    'name': 'La Clinique Extension',
    'version': '14.0.1',
    'category': '',
    'summary': 'La Clinique Extension',
    
    'author': 'SSL',
    'website': '',
    'maintainer': '',

    'depends': ['base','sale','product','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/bin_location_view.xml',
        'views/product_profile_view.xml',
        'views/partner.xml',
        'views/product.xml',
        'views/sale_view.xml',
        'views/purchase.xml',
    ],
    'installable': True,
    'auto_install': False,
    'price': 110.00,
    'currency': 'EUR',
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
}
