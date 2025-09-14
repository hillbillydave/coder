# connector.py
class FakeElm327Connector:
    def get_vin(self):
        return "1HGCM82633A004352"
    def get_dtcs(self):
        return ["P0300", "P0420"]

class FakeJ2534Connector:
    def get_vin(self):
        return "1HGCM82633A004352"
    def get_dtcs(self):
        return ["P0301", "P0421"]
