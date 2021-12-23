
class AnchoredPart(Part, ABC):
    """
    Base class for Anchored Parts.

    An Anchored part is attached to an other Part (anchor).
    They are joined at a single point.
    A Part can never collide with its Anchor.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        anchor: Part,
        position_anchor: Tuple[float, float] = (0, 0),
        position_part: Tuple[float, float] = (0, 0),
        rotation_range: float = math.pi / 4,
        angle_offset: float = 0,
        can_absorb: bool = False,
        movable: bool = True,
        **kwargs,
    ):
        """

        Args:
            anchor:
            position_anchor:
            position_part:
            rotation_range:
            angle_offset:
            can_absorb:
            movable:
            **kwargs:
        """

        Part.__init__(self, can_absorb=can_absorb, movable=movable, **kwargs)

        self._anchor: Part = anchor
        self._angle_offset = angle_offset
        self._rotation_range = rotation_range

        self._rel_coord_anchor = pymunk.Vec2d(*position_anchor)
        self._rel_coord_part = pymunk.Vec2d(*position_part)

        self.set_relative_coordinates()
        self._attach_to_anchor()

    @property
    def anchor(self):
        return self._anchor

    def _attach_to_anchor(self):
        self._joint = pymunk.PivotJoint(self._anchor.pm_body, self.pm_body,
                                        self._rel_coord_anchor,
                                        self._rel_coord_part)
        self._joint.collide_bodies = False
        self._limit = pymunk.RotaryLimitJoint(
            self._anchor.pm_body, self._pm_body,
            self._angle_offset - self._rotation_range / 2,
            self._angle_offset + self._rotation_range / 2)

        self._motor = pymunk.SimpleMotor(self.anchor.pm_body, self.pm_body, 0)

    def set_relative_coordinates(self):
        """
        Calculates the position of a Part relative to its Anchor.
        Sets the position of the Part.
        """

        self._pm_body.position = self._anchor.position\
            + self._rel_coord_anchor.rotated(self.anchor.angle)\
            - self._rel_coord_part.rotated(
                self._anchor.angle + self._angle_offset)
       
        self._pm_body.angle = self.anchor.pm_body.angle + self._angle_offset

    def reset(self):
        pass


