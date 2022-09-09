import faebryk
from faebryk.library.core import Component
from faebryk.library.library.interfaces import Electrical, Power
from faebryk.library.library.components import LED, Resistor
from faebryk.library.library.parameters import Constant, TBD


class LED_currentlimited(Component):
    def __init__(self) -> None:
        super().__init__()

        self.CMPs.led = LED()
        self.CMPs.led.set_forward_parameters(TBD(), TBD()) #TODO
        self.CMPs.current_limiting_resistor = Resistor(self.CMPs.led.needed_series_resistance_ohm(None, None, None)) #TODO

        self.IFs.power = Power()
        self.IFs.power.IFs.hv.connect(self.CMPs.led.IFs.anode) #TODO
        self.IFs.power.IFs.lv.connect(self.CMPs.current_limiting_resistor.IFs.next())
        self.CMPs.led.IFs.cathode.connect(self.CMPs.current_limiting_resistor.IFs.next()) #TODO

class LED_Driver(Component):
    def __init__(self, threshold_voltage_V) -> None:
        super().__init__()

        self.IFs.input_digital = Electrical()
        self.IFs.input_power = Power()
        
        self.CMPs.mosfet = None
        self.CMPs.led = LED_currentlimited()

        self.CMPs.mosfet.IFs.drain.connect(self.IFs.input_power.IFs.lv)
        self.CMPs.mosfet.IFs.gate.connect(self.IFs.input_digital)
        self.CMPs.led.IFs.power.IFs.lv.connect(self.CMPs.mosfet.IFs.source)
        self.CMPs.led.IFs.power.IFs.hv.connect(self.IFs.input_power.IFs.hv)

class LED_Indicator(Component):
    def __init__(self, threshold_voltage_V) -> None:
        super().__init__()

        self.IFs.input_digital = Electrical()
        self.IFs.input_power = Power()

        self.CMPs.led = LED_Driver(threshold_voltage_V)
        
        self.CMPs.led.IFs.input_power.connect(self.IFs.input_power)
        self.CMPs.led.IFs.input_digital.connect(self.IFs.input_digital)

# -----------------------------------------------------------------------------

class VoltageRegulator(Component):
    def __init__(self) -> None:
        super().__init__()

class DC_UPS(Component):
    #TODO params should be in builder
    # constructor gets direct references to submodules
    def __init__(
        self,
        input_voltage_min_V,
        input_voltage_max_V,
        output_voltage_V,
        peak_current_mA,
        duration_s,
        outage_current_mA,  
        cell_preference,
    ) -> None:
        super().__init__()

        # interfaces
        self.IFs.output_power_dc = Power()
        self.IFs.input_power_dc = Power()

        # submodules
        self.CMPs.input_power_adjustment = VoltageRegulator()
        self.CMPs.energy_storage = None
        self.CMPs.output_power_adjustment = VoltageRegulator()
        self.CMPs.redundant_power_mux = None

        # fabric
        self.CMPs.energy_storage.IFs.input_power.connect(self.IFs.input_power_dc)
        self.CMPs.redundant_power_mux.IFs.input_power.next.connect(self.IFs.input_power_dc)
        self.CMPs.redundant_power_mux.IFs.input_power.next.connect(self.CMPs.energy_storage.IFs.output_power)
        self.CMPs.redundant_power_mux.IFs.output_power.connect(self.IFs.output_power_dc)


class UI(Component):
    def __init__(self, ups: DC_UPS) -> None:
        super().__init__()

        self.ups = ups
        self.CMPs.outage_indicator = LED_Indicator(None) #TODO

        #TODO        
