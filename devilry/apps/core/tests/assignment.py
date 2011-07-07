from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from ..models import Period, Assignment, AssignmentGroup

class TestAssignment(TestCase):
    fixtures = ['core/deprecated_users.json', 'core/core.json']

    def test_unique(self):
        n = Assignment(parentnode=Period.objects.get(short_name='looong'),
                short_name='oblig1', long_name='O1',
                publishing_time=datetime.now())
        self.assertRaises(IntegrityError, n.save)

    def test_where_is_admin(self):
        ifiadmin = User.objects.get(username='ifiadmin')
        self.assertEquals(Assignment.where_is_admin(ifiadmin).count(), 3)

    def test_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        q = Assignment.where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'oblig1')
        ag = AssignmentGroup.objects.get(pk=4)
        ag.examiners.add(examiner1)
        ag.save()
        q = Assignment.where_is_examiner(examiner1)
        self.assertEquals(q.count(), 2)

    def test_published_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')

        q = Assignment.published_where_is_examiner(examiner1, old=False,
                active=False)
        self.assertEquals(q.count(), 0)

        q = Assignment.published_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'oblig1')

        ag = AssignmentGroup.objects.get(pk=4)
        ag.examiners.add(examiner1)
        ag.save()
        q = Assignment.published_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 2)

        ag.parentnode.publishing_time = datetime.now() + timedelta(10)
        ag.parentnode.save()
        q = Assignment.published_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)

    def test_active_where_is_examiner(self):
        future = datetime.now() + timedelta(10)
        examiner1 = User.objects.get(username='examiner1')
        q = Assignment.active_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'oblig1')

        ag = AssignmentGroup.objects.get(pk=4)
        ag.examiners.add(examiner1)
        ag.save()
        q = Assignment.active_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)
        ag.parentnode.parentnode.end_time = future
        ag.parentnode.parentnode.save()
        self.assertEquals(q.count(), 2)

        ag.parentnode.publishing_time = future
        ag.parentnode.save()
        q = Assignment.active_where_is_examiner(examiner1)
        self.assertEquals(q.count(), 1)

    def test_old_where_is_examiner(self):
        past = datetime.now() - timedelta(10)
        examiner3 = User.objects.get(username='examiner3')
        q = Assignment.old_where_is_examiner(examiner3)
        self.assertEquals(q.count(), 1)
        self.assertEquals(q[0].short_name, 'oldone')

        ag = AssignmentGroup.objects.get(pk=1)
        ag.examiners.add(examiner3)
        ag.save()
        q = Assignment.old_where_is_examiner(examiner3)
        self.assertEquals(q.count(), 1)
        ag.parentnode.parentnode.end_time = past
        ag.parentnode.parentnode.save()
        self.assertEquals(q.count(), 2)


    def test_assignmentgroups_where_is_examiner(self):
        examiner1 = User.objects.get(username='examiner1')
        examiner2 = User.objects.get(username='examiner2')
        oblig1 = Assignment.objects.get(id=1)
        self.assertEquals(3,
                oblig1.assignment_groups_where_is_examiner(examiner2)[0].id)
        self.assertEquals(2,
                oblig1.assignment_groups_where_is_examiner(examiner1).count())

    def test_assignmentgroups_where_is_examiner_or_admin(self):
        examiner1 = User.objects.get(username='examiner1')
        ifiadmin = User.objects.get(username='ifiadmin')

        oblig1 = Assignment.objects.get(id=1)
        self.assertEquals(1,
                oblig1.assignment_groups_where_can_examine(examiner1)[0].id)
        self.assertEquals(2,
                oblig1.assignment_groups_where_can_examine(examiner1).count())

        self.assertEquals(1,
                oblig1.assignment_groups_where_can_examine(ifiadmin)[0].id)
        self.assertEquals(4,
                oblig1.assignment_groups_where_can_examine(ifiadmin).count())

    def test_clean_publishing_time_before(self):
        oblig1 = Assignment.objects.get(id=1)
        oblig1.parentnode.start_time = datetime(2010, 1, 1)
        oblig1.parentnode.end_time = datetime(2011, 1, 1)
        oblig1.publishing_time = datetime(2010, 1, 2)
        oblig1.clean()
        oblig1.publishing_time = datetime(2009, 1, 1)
        self.assertRaises(ValidationError, oblig1.clean)

    def test_clean_publishing_time_after(self):
        oblig1 = Assignment.objects.get(id=1)
        oblig1.parentnode.start_time = datetime(2010, 1, 1)
        oblig1.parentnode.end_time = datetime(2011, 1, 1)
        oblig1.publishing_time = datetime(2010, 1, 2)
        oblig1.clean()
        oblig1.publishing_time = datetime(2012, 1, 1)
        self.assertRaises(ValidationError, oblig1.clean)

    def test_get_path(self):
        oblig1 = Assignment.objects.get(id=1)
        self.assertEquals(oblig1.get_path(), 'inf1100.looong.oblig1')

    def test_get_full_path(self):
        oblig1 = Assignment.objects.get(id=1)
        self.assertEquals(oblig1.get_full_path(),
                'uio.ifi.inf1100.looong.oblig1')

    def test_get_by_path(self):
        self.assertEquals(
                Assignment.get_by_path('inf1100.looong.oblig1').short_name,
                'oblig1')
        self.assertRaises(Assignment.DoesNotExist, Assignment.get_by_path,
                'does.not.exist')
        self.assertRaises(ValueError, Assignment.get_by_path, 'does.not')


    def test_pointscale(self):
        student1 = User.objects.get(username='student1')
        teacher1 = User.objects.get(username='teacher1')
        test = Assignment(parentnode = Period.objects.get(pk=1),
                          publishing_time = datetime.now(),
                          anonymous = False,
                          autoscale = True,
                          maxpoints = 1,
                          grade_plugin = "grade_approved:approvedgrade")
        test.save()
        self.assertEquals(test.pointscale, 1)
        self.assertEquals(test.maxpoints, 1)

        a = test.assignmentgroups.create(name="a")
        b = test.assignmentgroups.create(name="b")
        c = test.assignmentgroups.create(name="c")
        for assignmentgroup, points in ((a, 1), (b, 1), (c, 0)):
            delivery = assignmentgroup.deliveries.create(delivered_by=student1, successful=True)
            delivery.feedbacks.create(rendered_view="", grade="ok", points=points,
                                      is_passing_grade=bool(points),
                                      saved_by=teacher1)

        # With autoscale
        points = [g.points for g in test.assignmentgroups.all()]
        self.assertEquals(points, [1, 1, 0])
        scaled_points = [g.scaled_points for g in test.assignmentgroups.all()]
        self.assertEquals(scaled_points, [1.0, 1.0, 0.0])

        # With manual scale of 20
        test.autoscale = False
        test.pointscale = 20
        test.save()
        points = [g.points for g in test.assignmentgroups.all()]
        self.assertEquals(points, [1, 1, 0])
        scaled_points = [g.scaled_points for g in test.assignmentgroups.all()]
        self.assertEquals(scaled_points, [20.0, 20.0, 0.0])