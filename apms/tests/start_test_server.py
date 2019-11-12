import math
import random

from apms.server.server import ApmsServer


class TestServerAMPS:
    def test_updater(self, session_factory, test_config, fake_user_maker, image_maker):
        users = [fake_user_maker.make() for _ in range(5)]
        widths = (360, 720, 1080)
        heights = (math.ceil(360 / 1.5), math.ceil(720 / 1.5), math.ceil(1080 / 1.5))
        with session_factory.make_session() as session:
            for user in users:
                for _ in range(10):
                    photo = image_maker.make(
                        random.choice(widths), random.choice(heights)
                    )
                    photo.owner = user
                    photo.people = [random.choice(users)]
                session.add(user)
                session.add(photo)
            image_maker.save()

        server = ApmsServer(test_config)
        server.run()
