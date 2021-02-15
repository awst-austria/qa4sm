class Dto(object):
    def __create_attrs__(self, attributes):
        for attr in attributes:
            setattr(self, attr, None)
