from unittest.mock import patch

from .base import BaseFunctionalTestCase

from barbarian.events import Event, EventType
from barbarian.systems.visibility import spot_entities



@patch.object(Event, 'emit')
class TestSpotEntities(BaseFunctionalTestCase):

    dummy_map = [
        '#####.####',
        '#........#',
        '#....#...#',
        '#........#',
        '##########',
    ]

    def test_spot_entities(self, mock_emit):

        level = self.build_dummy_level()
        actor = self.spawn_actor(4, 2, 'player')

        a_to_spot = self.spawn_actor(1, 4, 'orc')
        level.actors.add_e(a_to_spot)

        p_to_spot = self.spawn_prop(3, 4, 'trap')
        level.props.add_e(p_to_spot)

        level.enter(actor)

        spot_entities(actor, level)

        self.assertEqual(2, mock_emit.call_count)
        mock_emit.assert_any_call(
            EventType.ACTOR_SPOTTED,
            event_data={'spotter': actor, 'spotted': a_to_spot})
        mock_emit.assert_any_call(
            EventType.ACTOR_SPOTTED,
            event_data={'spotter': actor, 'spotted': p_to_spot})

    def test_spot_entities_no_fov(self, mock_emit):

        level = self.build_dummy_level()
        actor = self.spawn_actor(4, 2, 'kobold')

        a_to_spot = self.spawn_actor(1, 4, 'orc')
        level.actors.add_e(a_to_spot)

        p_to_spot = self.spawn_prop(3, 4, 'trap')
        level.props.add_e(p_to_spot)

        level.enter(actor)

        spot_entities(actor, level)

        mock_emit.assert_not_called()

    def test_no_spot_entities_not_in_los(self, mock_emit):

        level = self.build_dummy_level()
        actor = self.spawn_actor(4, 2, 'player')

        # Actor hidden on the other side of the central pillar
        a_to_spot = self.spawn_actor(6, 2, 'player')
        level.actors.add_e(a_to_spot)

        level.enter(actor)

        spot_entities(actor, level)

        mock_emit.assert_not_called()

    def test_no_spot_entities_out_of_fov_range(self, mock_emit):

        level = self.build_dummy_level()
        actor = self.spawn_actor(4, 2, 'player')
        actor.fov.range = 2

        a_to_spot = self.spawn_actor(1, 1, 'kobold')
        level.actors.add_e(a_to_spot)

        level.enter(actor)

        spot_entities(actor, level)

        mock_emit.assert_not_called()
