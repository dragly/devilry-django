from django.utils.translation import ugettext as _

from devilry.core import gradeplugin_registry
from devilry.xmlrpc.gradeconf import GradeConf

from gradeviews import view
from models import CharFieldGrade


gradeplugin_registry.register(
        view = view,
        xmlrpc_gradeconf = GradeConf(),
        model_cls = CharFieldGrade,
        label = _('Manual grade handling'),
        description = _('Examiners type in grades manually in a text field ' \
            'without any restrictions beyond a 20 character limit.'))
