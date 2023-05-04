class CommunicationManagementMixin:
    def _transmit_messages(self, messages):

        msgs = {agent: {} for agent in self.agents}

        all_sent_messages = [
            (agent, comm_source, target)
            for agent, comms_dict in messages.items()
            for comm_source, target in comms_dict.items()
        ]

        for agent, comm_source, target in all_sent_messages:

            assert comm_source.agent is agent

            comm_target, message = target
            msg = comm_source.send(message)

            if not msg:
                continue

            if isinstance(comm_target, list):

                for targ in comm_target:
                    assert isinstance(targ, Communicator)
                    received_msg = targ.receive(comm_source, msg)

                    if received_msg:
                        msgs[targ.agent][targ] = (comm_source, received_msg)

            elif isinstance(comm_target, Communicator):
                received_msg = comm_target.receive(comm_source, msg)

                if received_msg:
                    msgs[comm_target.agent][comm_target] = (comm_source, received_msg)

            elif comm_target is None:
                for agent in self.agents:
                    for comm in agent.communicators:
                        received_msg = comm.receive(comm_source, msg)
                        if received_msg:
                            msgs[comm.agent][comm] = (comm_source, received_msg)

            else:
                raise ValueError

        return msgs
