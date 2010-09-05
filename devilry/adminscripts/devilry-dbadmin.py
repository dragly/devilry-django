#!/usr/bin/env python

from optparse import OptionParser
import logging

from common import (setup_logging, load_devilry_plugins, add_debug_opt,
    add_quiet_opt, add_settings_option, set_django_settings_module)


extra_help = """


"""


p = OptionParser(
        usage = "%prog [options] <action>")
add_settings_option(p)
p.add_option("--djangoadmin-script", dest="djangoadmin",
        default='django-admin.py',
        help="Path to the django-admin.py script. Defaults to "\
            "'django-admin.py', which means that it must be on the PATH.",
            metavar="PATH")
p.add_option("--no-backup-on-restore", action="store_false",
    dest="backup_on_restore", default=True,
    help="Normally a backup is made before a restore (because restore "\
        "destroys data). Use this to skip the backup.")
add_quiet_opt(p)
add_debug_opt(p)
(opt, args) = p.parse_args()
setup_logging(opt)

# Django must be imported after setting DJANGO_SETTINGS_MODULE
set_django_settings_module(opt)
load_devilry_plugins()
from devilry.core.models import Feedback, Assignment
from devilry.core.gradeplugin import GradePluginDoesNotExistError, \
    WrongContentTypeError, GradePluginError


def exit_help(msg=""):
    p.print_help()
    print
    print extra_help
    raise SystemExit(msg)

def validate_gradeplugins():
    for assignment in Assignment.objects.all():
        try:
            assignment.validate_gradeplugin()
        except GradePluginDoesNotExistError, e:
            logging.error("%s: %s" % (assignment, str(e)))
        else:
            logging.info('%-70s  [ OK ]' % assignment)

def validate_gradeplugin_contenttypes():
    for feedback in Feedback.objects.all():
        try:
            feedback.validate_gradeobj()
        except GradePluginError, e:
            logging.error("%s: %s" % (feedback, str(e)))
        else:
            logging.info("%-70s  [ OK ]" % feedback)


if len(args) == 0:
    exit_help()
action = args[0]

if action == "fix-gradeplugin-content-type-errors":
    for feedback in Feedback.objects.all():
        try:
            feedback.validate_gradeobj()
        except GradePluginDoesNotExistError, e:
            logging.error("%s: %s" % (feedback, str(e)))
        except WrongContentTypeError, e:
            assignment = feedback.delivery.assignment_group.parentnode
            correct_ct = assignment.get_gradeplugin_registryitem().get_content_type()
            feedback.content_type = correct_ct
            feedback.save()
            logging.warning("%-70s: Content type changed to: id: %s (%s)." % (
                feedback, correct_ct.pk, correct_ct))
        else:
            logging.debug("%-70s  [ NO CHANGE REQUIRED ]" % feedback)

elif action == "validate-gradeplugins":
    validate_gradeplugins()
elif action == "validate-gradeplugin-content-types":
    validate_gradeplugin_contenttypes()
else:
    exit_help("ERROR: Invalid action.")