from django.db import models
from django.test import TestCase

from cheaptrees.anybase import Encoder, EncoderException, needed_bits
from cheaptrees.models import Thread, Node


class Comment(Node):
    text = models.TextField()


class TestEncoding(TestCase):

    def test_needed_bits(self):
        self.assertEquals(needed_bits(10), 4)
        self.assertEquals(needed_bits(64), 6)
        self.assertEquals(needed_bits(4096), 12)

    def test_init(self):
        encoder = Encoder(base=24)
        self.assertEquals(encoder.base, 24)
        self.assertEquals(encoder.digits, 1)

    def test_init_64(self):
        encoder = Encoder(base=64)
        self.assertEquals(encoder.base, 64)
        self.assertEquals(encoder.digits, 1)

    def test_init_4096(self):
        encoder = Encoder(base=4096)
        self.assertEquals(encoder.base, 4096)
        self.assertEquals(encoder.digits, 2)

    def test_encode(self):
        encoder = Encoder(base=10)
        self.assertEquals('4', encoder.encode(4))

    def test_decode(self):
        encoder = Encoder(base=10)
        self.assertEquals(4, encoder.decode('4'))

    def test_encode_decode_64(self):
        encoder = Encoder(base=64)
        self.assertEquals('R', encoder.encode(34))
        self.assertEquals('o', encoder.encode(63))
        for n in range(0, 64):
            self.assertEquals(n, encoder.decode(encoder.encode(n)))

    def test_base_4096(self):
        encoder = Encoder(base=4096)
        self.assertEquals(encoder.digits, 2)
        self.assertEquals('00', encoder.encode(0))
        self.assertEquals('0R', encoder.encode(34))
        self.assertEquals('R0', encoder.encode(34 * 64))
        self.assertEquals('oo', encoder.encode(4095))
        all_encodings = set()
        for n in range(0, 4096):
            encoded = encoder.encode(n)
            self.assertEquals(n, encoder.decode(encoded))
            all_encodings.add(encoded)
        self.assertEquals(len(all_encodings), 4096)

    def test_decoding_errors_base_4096(self):
        encoder = Encoder(base=4096)
        self.assertRaises(EncoderException, encoder.decode, 'o')
        self.assertRaises(EncoderException, encoder.decode, '0AR')
        self.assertRaises(EncoderException, encoder.decode, '  ')


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
        self.assertEqual(comment.text, 'Hi')
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
        child = comment.create_child(text='I cannot agree less')
        self.assertEqual(comment.children.count(), 4)
        self.assertEqual(child.locator, '03')
        self.assertEqual(child.children.count(), 0)
        fetched_child = Comment.objects.get(locator='03')
        self.assertEqual(fetched_child.text, 'I cannot agree less')
