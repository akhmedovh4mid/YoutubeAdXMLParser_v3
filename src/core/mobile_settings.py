from uiautomator2 import Device


class MobileSettings:
    def __init__(self, device: Device) -> None:
        self._device = device
        
    def notification_enable(self) -> None:
        self._device.shell(["cmd", "notification", "set_dnd", "off"])
    
    def notification_disable(self) -> None:
        self._device.shell(["cmd", "notification", "set_dnd", "on"])
        
    def change_rotation(self) -> None:
        self._device.shell(["settings", "put", "system", "user_rotation", "0"])
