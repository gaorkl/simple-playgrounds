from simple_playgrounds.agent.part.part import AnchoredPart


class Arm(AnchoredPart):
    """
    Rectangular Part, attached on one extremity.
    Is colliding with other Entity or Part, except from anchor and other Parts attached to it.

    Attributes:
        extremity_anchor_point: coordinates of the free extremity, used to attach other Parts.

    """
    def __init__(self, anchor, position_anchor, angle_offset=0, **kwargs):
        default_config = parse_configuration('agent_parts', PartTypes.ARM)
        body_part_params = {**default_config, **kwargs}

        # arm attached at one extremity, and other anchor point defined at other extremity
        width, length = body_part_params['size']
        position_part = (-length / 2.0 + width / 2.0, 0)
        self.extremity_anchor_point = (+length / 2.0 - width / 2.0, 0)

        super().__init__(anchor=anchor,
                         position_anchor=position_anchor,
                         position_part=position_part,
                         angle_offset=angle_offset,
                         **body_part_params)

        self.motor.max_force = ARM_MAX_FORCE


