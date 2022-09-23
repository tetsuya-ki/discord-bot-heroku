class Members:

    def __init__(self):
        self.members = [] # ゲームに参加しているメンバー
        self.len = 0
        self.minutes = 2

    def add_member(self, member):
        self.members.append(member)
        self.members = list(set(self.members))
        self.len = len(self.members)

    def remove_member(self, member):
        self.members = [s for s in self.members if s != member]
        self.len = len(self.members)

    def set_minutes(self, minutes):
        self.minutes = minutes

    def add_minutes(self, minutes):
        if minutes is not None and str(minutes).isdecimal():
            self.minutes + minutes

    def get_members(self):
        return self.members