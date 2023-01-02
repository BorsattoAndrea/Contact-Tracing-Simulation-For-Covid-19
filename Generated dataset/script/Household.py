class Household:
    def __init__(self, id, members, address):
        self.id = id
        self.members = members
        self.address = address

    def __repr__(self):
        return  "Household(id:" + str(self.id) + ", members: " + str(self.members) + ")"