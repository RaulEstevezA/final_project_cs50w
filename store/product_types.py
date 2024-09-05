# file to update product categories

from .models import Motherboard, CPU, GraphicsCard, RAM, ComputerCase, PowerSupply, CPUAirCooler, CPULiquidCooler, CaseFan, SoundCard, HardDrive, SSD, Monitor, Keyboard, Headset, Mouse, WebCam

# List of all product models
PRODUCT_MODELS = [
    Motherboard, CPU, GraphicsCard, RAM, ComputerCase, PowerSupply,
    CPUAirCooler, CPULiquidCooler, CaseFan, SoundCard, HardDrive,
    SSD, Monitor, Keyboard, Headset, Mouse, WebCam
]

# Dictionary to map category names to models
# When adding new products, if the category has more than one word add the space on the left side
CATEGORY_TO_MODEL = {
    'Motherboards': Motherboard,
    'CPUs': CPU,
    'Graphics Cards': GraphicsCard,
    'RAM': RAM,
    'Computer Cases': ComputerCase,
    'Power Supplies': PowerSupply,
    'CPU Air Coolers': CPUAirCooler,
    'CPU Liquid Coolers': CPULiquidCooler,
    'Case Fans': CaseFan,
    'SoundCards': SoundCard,
    'Hard Drives': HardDrive,
    'SSDs': SSD,
    'Monitors': Monitor,
    'Keyboards': Keyboard,
    'Headsets': Headset,
    'Mouses': Mouse,
    'WebCams': WebCam
}
