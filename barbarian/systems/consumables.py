"""
Handle charged, entities.

"""
import logging


logger = logging.getLogger(__name__)


def consume_entity(event_data, last_action=None):
    """
    Decrement entity charges by one and run optional logic if it reaches zero,
    depending ot its type.

    No-op is entity is not consumable.

    """
    e = event_data['entity']
    if not e.consumable:
        logger.debug('Entity %s has no Consumable component', e)
        return

    if last_action and not last_action.valid:
        logger.debug(
            'Last action (typs <%s>) was rejected: skip depleting charges.', 
            last_action)
        return

    e.consumable.charges -= 1

    if e.consumable.depleted:
        if (e.item and
            (owner := event_data.get('owner', None)) and
            owner.inventory
        ):
            owner.inventory.items.remove(e)