import unittest

from barbarian.events import Event, EventType


class TestEvents(unittest.TestCase):

    def setUp(self):
        Event._QUEUE = []
        Event._LOG = {}

    def test_emit(self):
        e = Event.emit(EventType.ACTION_ACCEPTED, msg='woo!')
        self.assertEqual(1, len(Event._QUEUE))
        self.assertIn(e, Event._QUEUE)
        self.assertEqual(1, len(Event._LOG['current']))
        self.assertIn(e, Event._LOG['current'])

    def test_clear_queue(self):
        Event.emit(EventType.ACTION_ACCEPTED, msg='woo!', transient=False)
        Event.emit(EventType.ACTION_ACCEPTED, msg='woo!', transient=True)
        self.assertEqual(2, len(Event._QUEUE))

        Event.clear_queue()
        self.assertEqual(0, len(Event._QUEUE))


    def test_flush_log(self):
        e1 = Event.emit(
            EventType.ACTION_ACCEPTED, msg='woo!', transient=False)
        e2 = Event.emit(
            EventType.ACTION_REJECTED, msg='ono!', transient=False)

        self.assertEqual(2, len(Event._LOG['current']))

        tick1 = 1
        Event.flush_log(tick1)

        self.assertEqual(0, len(Event._LOG['current']))
        self.assertEqual(2, len(Event._LOG[tick1]))
        self.assertIn(e1, Event._LOG[tick1])
        self.assertIn(e2, Event._LOG[tick1])

        e3 = Event.emit(
            EventType.ACTION_ACCEPTED, msg='woo again!', transient=False)
        tick2 = 2
        Event.flush_log(tick2)

        self.assertEqual(0, len(Event._LOG['current']))
        self.assertEqual(1, len(Event._LOG[tick2]))

        self.assertIn(e1, Event._LOG[tick1])
        self.assertIn(e2, Event._LOG[tick1])
        self.assertIn(e3, Event._LOG[tick2])

    def test_transient_events_are_not_kept_in_the_log(self):
        e = Event.emit(
            EventType.ACTION_ACCEPTED, msg='woo!', transient=True)

        self.assertEqual(1, len(Event._LOG['current']))

        tick = 1
        Event.flush_log(tick)

        self.assertEqual(0, len(Event._LOG['current']))
        self.assertNotIn(tick, Event._LOG)

    def test_get_current_events(self):
        events = [
            Event.emit(
                EventType.ACTION_ACCEPTED, msg='woo!', transient=True),
            Event.emit(
                EventType.ACTION_REJECTED, msg='ono!', transient=True),
        ]

        current_events = Event.get_current_events(1)
        self.assertListEqual(events, current_events)
        self.assertEqual(2, len(Event._LOG['current']))

    def test_get_current_events_and_flush(self):
        events = [
            Event.emit(
                EventType.ACTION_ACCEPTED, msg='woo!', transient=True),
            Event.emit(
                EventType.ACTION_REJECTED, msg='ono!', transient=False),
        ]

        current_events = Event.get_current_events(1, flush=True)
        self.assertListEqual(events, current_events)
        self.assertEqual(0, len(Event._LOG['current']))
        self.assertEqual(1, len(Event._LOG[1]))

    def test_serialize(self):
        e = Event.emit(
            EventType.ACTOR_DIED, msg='hello', event_data={'key': 'val'})

        expected = {
            'type': 'actor_died',
            'msg': 'hello',
            'data': {'key': 'val'},
        }
        self.assertDictEqual(expected, e.serialize())
