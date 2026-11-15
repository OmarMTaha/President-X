"""A unit at the table, and a clone built on top of that unit.

Unit holds the three facts every seated person shares.
Clone is a Unit: it inherits the chair, and adds the lock.
Attributes are created in __init__, so each clone has its own.
"""


class Unit:
    """One seated person: an id, a short code and a chair number."""

    def __init__(self, unit_id, code, seat):
        """Store who this is and which chair they sit in.

        Precondition: seat is 0, 1 or 2.
        """
        self.id = unit_id
        self.code = code
        self.seat = seat

    def __str__(self):
        """Return the nameplate under the chair."""
        return f"UNIT 0{self.seat + 1}  /  {self.code}"


class Clone(Unit):
    """A printed copy of the President. A Clone is a Unit with a body and a lock."""

    def __init__(self, unit_id, code, seat):
        """Build the unit, then clear the lock and the question count."""
        super().__init__(unit_id, code, seat)
        self.reset()

    def reset(self):
        """Clear the lock, the shock and how many questions this unit has heard."""
        self.hostile = False
        self.shocked = False
        self.shock_anim = 0.0
        self.asked_count = 0
        self.glitch = 0.0
        self.eyes = "auto"
