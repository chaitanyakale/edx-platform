 # coding=utf-8

import mock
import logging

import ddt
from courseware.management.commands.dump_to_neo4j import (
    ModuleStoreSerializer,
    ITERABLE_NEO4J_TYPES,
)
from django.core.management import call_command
from xmodule.modulestore.tests.django_utils import SharedModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory

log = logging.getLogger(__name__)


class TestDumpToNeo4jCommandBase(SharedModuleStoreTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestDumpToNeo4jCommandBase, cls).setUpClass()
        cls.course = CourseFactory.create()
        cls.chapter = ItemFactory.create(parent=cls.course, category='chapter')
        cls.sequential = ItemFactory.create(parent=cls.chapter, category='sequential')
        cls.vertical = ItemFactory.create(parent=cls.sequential, category='vertical')
        cls.html = ItemFactory.create(parent=cls.vertical, category='html')
        cls.problem = ItemFactory.create(parent=cls.vertical, category='problem')
        cls.video = ItemFactory.create(parent=cls.vertical, category='video')
        cls.video2 = ItemFactory.create(parent=cls.vertical, category='video')

        cls.course2 = CourseFactory.create()

class TestDumpToNeo4jCommand(TestDumpToNeo4jCommandBase):
    """
    Tests for the dump to neo4j management command
    """
    def setUp(self):
        super(TestDumpToNeo4jCommand, self).setUp()

    @mock.patch('courseware.management.commands.dump_to_neo4j.Graph')
    def test_dump_to_neo4j(self, MockGraph):
        """
        Tests the dump_to_neo4j management command works against a mock
        py2neo Graph
        """
        mock_graph = MockGraph.return_value
        mock_transaction = mock.Mock()
        mock_graph.begin.return_value = mock_transaction

        call_command('dump_to_neo4j')

        self.assertEqual(mock_graph.delete_all.call_count, 1)
        self.assertEqual(mock_graph.begin.call_count, 2)
        self.assertEqual(mock_transaction.commit.call_count, 2)
        self.assertEqual(mock_transaction.rollback.call_count, 0)

        # 7 nodes + 9 relationships from the first course
        # 2 nodes and no relationships from the second
        self.assertEqual(mock_transaction.create.call_count, 18)

    @mock.patch('courseware.management.commands.dump_to_neo4j.Graph')
    def test_dump_to_neo4j_rollback(self, MockGraph):
        """
        Tests that the management command handles the case where there's
        an exception trying to write to the neo4j database.
        """
        mock_graph = MockGraph.return_value
        mock_transaction = mock.Mock()
        mock_graph.begin.return_value = mock_transaction
        mock_transaction.create.side_effect = ValueError('Something went wrong!')

        call_command('dump_to_neo4j')

        self.assertEqual(mock_graph.delete_all.call_count, 1)
        self.assertEqual(mock_graph.begin.call_count, 2)
        self.assertEqual(mock_transaction.commit.call_count, 0)
        self.assertEqual(mock_transaction.rollback.call_count, 2)


@ddt.ddt
class TestModuleStoreSerializer(TestDumpToNeo4jCommandBase):
    """
    Tests for the ModuleStoreSerializer
    """
    def setUp(self):
        super(TestModuleStoreSerializer, self).setUp()
        self.modulestore_serializer = ModuleStoreSerializer()

    def test_serialize_item(self):
        """
        Tests the _serialize_item method.
        """
        fields, label = self.modulestore_serializer._serialize_item(self.course)
        self.assertEqual(label, "course")
        self.assertIn("edited_on", fields.keys())
        self.assertIn("display_name", fields.keys())
        self.assertIn("org", fields.keys())
        self.assertIn("course", fields.keys())
        self.assertIn("run", fields.keys())
        self.assertIn("course_key", fields.keys())
        self.assertNotIn("checklist", fields.keys())

    def test_serialize_course(self):
        """
        Tests the serialize_course method.
        """
        nodes, relationships = self.modulestore_serializer.serialize_course(
            self.course.id
        )
        self.assertEqual(len(nodes), 9)
        self.assertEqual(len(relationships), 7)

    @ddt.data(*ITERABLE_NEO4J_TYPES)
    def test_coerce_types_iterable(self, iterable_type):
        """
        Tests the coerce_types helper method for iterable types
        """
        example_iterable = iterable_type([object, object, object])

        # each element in the iterable is not unicode:
        self.assertFalse(any(isinstance(tab, unicode) for tab in example_iterable))
        # but after they are coerced, they are:
        coerced = self.modulestore_serializer.coerce_types(example_iterable)
        self.assertTrue(all(isinstance(tab, unicode) for tab in coerced))
        # finally, make sure we haven't changed the type:
        self.assertEqual(type(coerced), iterable_type)

    @ddt.data(
        (1, 1),
        (object, u"<type 'object'>"),
        (1.5, 1.5),
        (u"úñîçø∂é", u"úñîçø∂é"),
        ("plain string", "plain string"),
        (True, True),
        (None, "None"),
    )
    @ddt.unpack
    def test_coerce_types_base(self, original_value, coerced_expected):
        """
        Tests the coerce_types helper for the neo4j base types
        """
        coerced_value = self.modulestore_serializer.coerce_types(original_value)
        self.assertEqual(coerced_value, coerced_expected)
