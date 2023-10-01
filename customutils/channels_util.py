import asyncio

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class ChannelsCommonConsumer:
    def send_data(self, data, room_group_name):
        try:
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(
                room_group_name, {"type": "send_notification", "text": data}
            )
        except Exception as e:
            exception = str(e)
            print(
                "Exception in Channels Consumers *************************************{}".format(
                    e
                )
            )
            # pass

    def wait_for_coro(self):
        try:
            loop = (
                asyncio.get_event_loop()
            )  # gets previously set event loop, if possible
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop
