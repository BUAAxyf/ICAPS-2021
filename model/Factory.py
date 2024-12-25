from model.Port import Port


class Factory:
    """
    A factory(customer) with several ports
    """
    def __init__(self, factory_id, longitude, latitude, port_num):
        # 属性
        self.factory_id = factory_id
        self.longitude = longitude
        self.latitude = latitude
        self.port_num = port_num

        # ports
        # self.queue_vehicles = [] # FIFO
        self.port_list = []
        self._init_ports()

    def __str__(self):
        return f"Factory({self.factory_id})"

    def _init_ports(self):
        """
        Initialize the ports of the factory
        """
        for i in range(self.port_num):
            port = Port()
            self.port_list.append(port)

    def _find_first_port(self):
        """
        Find the port finishing first
        """
        min_finish_time = float('inf')
        first_port = None
        for port in self.port_list:
            if port.finish_time < min_finish_time:
                min_finish_time = port.finish_time
                first_port = port
        return first_port, min_finish_time

    def add_vehicle(self, vehicle, operation):
        """
        Add a vehicle to the port finishing first
        """
        first_port, min_finish_time = self._find_first_port()
        if min_finish_time == 0:
            status = 'LOADING' if operation == 'PICK_UP' else 'UNLOADING'
        else:
            status = 'WAITING'
        # update port.finish_time
        first_port.finish_time += vehicle.current_assignment[1].load_time \
            if operation == 'PICK_UP' else vehicle.current_assignment[1].unload_time
        return status, first_port

