from django.db import models


BASE = 10
DIGITS = 1
DEPTH = 10


# naive base10 encodings
def encode(position):
    return chr(position + ord('0'))


def decode(encoded):
    return ord(encoded) - ord('0')


class Thread(models.Model):
    pass


class Node(models.Model):
    thread = models.ForeignKey(Thread)
    locator = models.CharField(max_length=DEPTH * DIGITS, db_index=True)
    #depth = models.IntegerField(editable=False)

    class Meta:
        abstract = True
        ordering = ['locator']
        unique_together = ('thread', 'locator')

    @property
    def manager(self):
        return self.__class__.objects

    @property
    def position(self):
        return decode(self.locator[DIGITS:])

    @property
    def parent_locator(self):
        return self.locator[:-DIGITS]

    @property
    def parent(self):
        if self.parent_locator == '':
            return None
        return self.manager.get(thread=self.thread,
                                locator=self.parent_locator)

    @property
    def descendants(self):
        family = self.manager.filter(locator__startswith=self.locator)
        return family.exclude(pk=self.pk)

    @property
    def children(self):
        regex = r'^.{%d}$' % (len(self.locator) + 1)
        return self.descendants.filter(locator__regex=regex)

    @property
    def last_child(self):
        last_child = self.children.reverse()[:1]
        if last_child:
            return last_child[0]
        return None

    @property
    def next_child_locator(self):
        last_child = self.last_child
        if last_child is None:
            next_ordinal = 0
        else:
            next_ordinal = decode(self.last_child.locator[-1:]) + 1
        return self.locator + encode(next_ordinal)

    def create_child(self, **kwargs):
        return self.manager.create(thread=self.thread,
                                   locator=self.next_child_locator,
                                   **kwargs)
