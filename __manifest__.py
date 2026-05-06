{
    'name': 'HR Hospital',
    'summary': '',
    'author': 'Odoo School',
    'website': 'https://odoo.school/',
    'category': 'Customizations',
    'license': 'OPL-1',
    'version': '19.0.2.2.0',

    'depends': [
        'base',
    ],

    'external_dependencies': {
        'python': [],
    },

    'data': [

        'security/ir.model.access.csv',

        'wizard/hr_hospital_mass_reassign_doctor_wizard_view.xml',
        'wizard/hr_hospital_visit_report_wizard_view.xml',
        'wizard/hr_hospital_disease_report_wizard_view.xml',

        'views/hr_hospital_menu.xml',
        'views/hr_hospital_doctor_views.xml',
        'views/hr_hospital_patient_views.xml',
        'views/hr_hospital_disease_views.xml',
        'views/hr_hospital_visit_views.xml',
        'views/hr_hospital_doctor_category_views.xml',
        'views/hr_hospital_doctor_history_views.xml',

        'data/hr_hospital_disease_data.xml',
        'data/hr_hospital_doctor_category_data.xml',
    ],
    'demo': [
        'demo/hr_hospital_doctor_demo.xml',
        'demo/hr_hospital_patient_demo.xml',
        'demo/hr_hospital_doctor_history_demo.xml',
        'demo/hr_hospital_visit_demo.xml',
        'demo/hr_hospital_disease_demo.xml'
    ],

    'installable': True,
    'auto_install': False,

    'images': [
        'static/description/icon.png'
    ],

}