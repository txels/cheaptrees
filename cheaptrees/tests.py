from django.db import models
from django.test import TestCase

from cheaptrees.models import encode, decode, Thread, Node


class Comment(Node):
    text = models.TextField()


class TestEncoding(TestCase):

    def test_encode(self):
        self.assertEquals('4', encode(4))

    def test_decode(self):
        self.assertEquals(4, decode('4'))


LOCATORS = ['11', '0', '1', '01', '00', '02', '111']


def get_locators(comments):
    return map(lambda x: getattr(x, 'locator'), comments)


class TestThreadedComment(TestCase):

    def setUp(self):
        thread = Thread.objects.create()
        for locator in LOCATORS:
            Comment.objects.create(thread=thread, locator=locator, text='Hi')

    def test_position(self):
        tc01 = Comment.objects.get(locator='01')
        self.assertEqual(tc01.position, 1)

    def test_thread(self):
        thread = Thread.objects.get()
        self.assertEqual(thread.comment_set.count(), len(LOCATORS))
        comments = Comment.objects.filter(thread_id=1)
        locators = get_locators(comments)
        self.assertEqual(sorted(LOCATORS), locators)

    def test_parent(self):
        comment = Comment.objects.get(locator='111')
        self.assertEqual(comment.parent.locator, '11')
        self.assertEqual(comment.parent.thread, comment.thread)
        self.assertEqual(comment.parent.parent.locator, '1')
        self.assertEqual(comment.parent.parent.parent, None)

    def test_children(self):
        comment = Comment.objects.get(locator='0')
        self.assertEqual(comment.children.count(), 3)
        locators = get_locators(comment.children)
        self.assertEqual(locators, ['00', '01', '02'])
        comment1 = Comment.objects.get(locator='1')
        self.assertEqual(comment1.children.count(), 1)
        locators = get_locators(comment1.children)
        self.assertEqual(locators, ['11'])
        locators = get_locators(comment1.children[0].children)
        self.assertEqual(locators, ['111'])

    def test_descendants(self):
        comment = Comment.objects.get(locator='0')
        self.assertEqual(comment.descendants.count(), 3)
        comment1 = Comment.objects.get(locator='1')
        self.assertEqual(comment1.descendants.count(), 2)
        locators = get_locators(comment1.descendants)
        self.assertEqual(locators, ['11', '111'])

    def test_last_child(self):
        comment = Comment.objects.get(locator='0')
        self.assertEqual(comment.last_child.locator, '02')

    def test_next_child_locator(self):
        comment = Comment.objects.get(locator='0')
        self.assertEqual(comment.next_child_locator, '03')
        comment = Comment.objects.get(locator='1')
        self.assertEqual(comment.next_child_locator, '12')
        comment = Comment.objects.get(locator='01')
        self.assertEqual(comment.next_child_locator, '010')

    def test_create_child(self):
        comment = Comment.objects.get(locator='0')
        self.assertEqual(comment.children.count(), 3)
        child = comment.create_child()
        self.assertEqual(comment.children.count(), 4)
        self.assertEqual(child.locator, '03')
        self.assertEqual(child.children.count(), 0)
