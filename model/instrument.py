from model.entity import Entity


class Instrument(Entity):

    def add_link(self, link):
        self.links.append(link)

    def add_image(self, image):
        self.images.append(image)

    def __init__(self, name, type, links=[], images=[]):
        super(Instrument, self).__init__()
        self.name = name
        self.type = type
        self.links = links
        self.images = images
