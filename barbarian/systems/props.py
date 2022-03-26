"""
Prop logic

"""
import logging

from barbarian.actions import Action, ActionType

logger = logging.getLogger(__name__)


def use_prop(action, level):
    """
    Handle a deliberate (ie, initited by an actor, via its ai
    or user input) use of a level prop.

    """
    actor, _, data = action.unpack()

    propx = data.get('propx', actor.pos.x)
    propy = data.get('propy', actor.pos.y)

    if prop := level.props[propx, propy]:
        if prop.usable:
            if (prop.usable.use_key and
                prop.usable.use_key != data['use_key']):
                return action.reject(msg="You can't do that here")
            action.accept()
            new_action_args = prop.usable.action
            new_action_args.update(
                prop.usable.get_actor_and_target(actor, prop))
            return Action.from_dict(new_action_args)
        else:
            logger.warning(
                'Trying to use prop with no use function: %s', prop)

    action.reject(msg="You can't do that here")


def trigger(actor, prop):
    """
    Handle an auto-trigerring prop, whether because an actor has
    entered its cell or because it has bumped into it.

    """
    assert prop.trigger

    action_args = prop.trigger.action
    action_args.update(prop.trigger.get_actor_and_target(actor, prop))
    return Action.from_dict(action_args)


def open_or_close_door(action, level):
    """
    Open of close the `target` entity, depending on its current state.

    """
    actor, door, _ = action.unpack()

    match action.type:

        case ActionType.OPEN_DOOR:

            if door.openable.open:
                return action.reject(msg='Door is already opened')

            door.physics.blocks = False
            door.physics.blocks_sight = False
            door.openable.open = True
            door.usable =  door.usable.new_action({'type': 'close_door'})

        case ActionType.CLOSE_DOOR:

            if not door.openable.open:
                return action.reject(msg='Door is already closed')

            x, y = door.pos.x, door.pos.y
            if level.is_blocked(x, y) or any(level.items[x, y]):
                return action.reject(
                    msg="Can't close door, something is blocking the way")

            door.physics.blocks = True
            door.physics.blocks_sight = True
            door.openable.open = False
            door.usable =  door.usable.new_action({'type': 'open_door'})

        case _:

            return action.reject(
                f'Expected action of type [OPEN|CLOSE]_DOOR, '
                f'got: {action.type}')

    action.accept()

    level.init_fov_map()
    if actor.fov:
        actor.fov.compute(
            level, actor.pos.x, actor.pos.y,
            update_level=actor.is_player)
