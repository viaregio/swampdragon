from .serializers import FooSerializer, BarSerializer, BazSerializer
from .models import FooModel, BarModel, BazModel
from ..tests.dragon_django_test_case import DragonDjangoTestCase


class DeserializerTest(DragonDjangoTestCase):
    def test_meta(self):
        serializer = FooSerializer()
        self.assertIn('test_field_a', serializer.opts.publish_fields)
        self.assertIn('test_field_a', serializer.opts.update_fields)
        self.assertIn('test_field_b', serializer.opts.update_fields)

    def test_deserialize_simple_model(self):
        """
        Deserialize a simple model with no relationships
        """
        data = {'test_field_a': 'foo', 'test_field_b': 'bar'}
        foo = FooSerializer(data=data).save()
        self.assertEqual('foo', foo.test_field_a)
        self.assertEqual('bar', foo.test_field_b)

    def test_deserialize_with_fk(self):
        """
        Deserialize a model with a foreign key
        """
        data = {
            'number': 12,
            'foo': {'test_field_a': 'foo', 'test_field_b': 'bar'}
        }
        bar = BarSerializer(data).save()
        self.assertEqual(bar.number, 12)
        self.assertEqual(bar.foo.test_field_a, 'foo')

    def test_deserialize_reverse_fks(self):
        """
        Deserialize a model with a list of reverse FKs
        """
        data = {
            'test_field_a': 'foo',
            'test_field_b': 'bar',
            'bars': [
                {'number': 52,},
                {'number': 42,},
            ]
        }
        serializer = FooSerializer(data)
        foo = serializer.save()
        self.assertTrue(foo.bars.exists())

    def test_deserialize_one_to_one(self):
        """
        Deserialize a model with a one to one relationship
        """
        data = {
            'name': 'this is baz',
            'bar': {'number': 25}
        }

        baz = BazSerializer(data).save()
        self.assertEqual(baz.name, 'this is baz')
        self.assertEqual(baz.bar.number, 25)


class SerializerTest(DragonDjangoTestCase):
    def test_serialize_simple_model(self):
        """
        Serialize a model with no FKs
        """
        foo = FooModel.objects.create(test_field_a='hello', test_field_b='world')
        serializer = FooSerializer(instance=foo)
        data = serializer.serialize()
        for pub_field in serializer.opts.publish_fields:
            self.assertIn(pub_field, data)

    def test_serialize_with_fk(self):
        """
        Serialize a model with a foreign key
        """
        foo = FooModel.objects.create(test_field_a='hello', test_field_b='world')
        bar = BarModel.objects.create(number=123, foo=foo)
        serializer = BarSerializer(instance=bar)
        data = serializer.serialize()
        self.assertEqual(data['foo']['test_field_a'], foo.test_field_a)

    def test_serialize_reverse_fks(self):
        """
        Serialize a model with a reverse foreign key.
        Make sure infinite recursion does not occur
        """
        foo = FooModel.objects.create(test_field_a='hello', test_field_b='world')
        foo.bars.add(BarModel.objects.create(number=123))
        foo.bars.add(BarModel.objects.create(number=333))
        serializer = FooSerializer(instance=foo)
        data = serializer.serialize()

    def test_serialize_one_to_one(self):
        """
        Serialize a model with a one to one relationship
        """
        bar = BarModel.objects.create(number=333)
        baz = BazModel.objects.create(name='bazzy', bar=bar)
        serializer = BazSerializer(instance=baz)
        data = serializer.serialize()
        self.assertEqual(data['bar']['number'], 333)
        self.assertEqual(data['name'], 'bazzy')
