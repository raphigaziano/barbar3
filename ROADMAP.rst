Features
========

  - items

    - spawn actors with items in their inventories
    - drop items on death
    - drop corpses
    - item identification (wait unti we have more item types, no real interest 
      until then).

  - Targeted actions

    Classics like magic missile and fireball spells should do the trick.
    This will require getting started on a spell data model, and possibly
    allow the game lib to request additional data before processing an action,
    which in turn involves refactoring the gameloop...

  - Save / Load

Internal
========

- Action validation
- Data driven action definitions ?
- Data driven component definitions ?

Testing
-------

- Start building test dataset and use it in functional tests.

Docs
----

- Action data
- "App protocol"

Bugfixes
========

- [client]: fix multiline logging multiline messages.
