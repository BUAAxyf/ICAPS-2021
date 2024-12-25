import copy


class Vehicle:
    """
    A vehicle
    """
    def __init__(self, car_num, capacity, operation_time, gps_id):
        # 属性
        self.car_num = car_num # unique
        self.capacity = capacity
        self.operation_time = operation_time
        self.gps_id = gps_id
        self.route = None

        # 历史状态(每次状态变化都记录)
        self.history_info = [('time', 'action', 'Factory_id', 'condition', 'next_status')] # list of (time, action, Factory, load), where action is 'PICK_UP' or 'DELIVER' or 'LOAD' or 'UNLOAD' or 'WAIT'
        self.delay = 0 # 延误时间
        self.distance = 0

        # 当前状态
        self.now = 0 # 当前时间
        self.current_assignment = None # (Factory_id, Order, operation)
        self.assignment_list = [] # list of (Factory_id, Order, operation), where operation is 'PICK_UP' or 'DELIVER'
        self.cargo = [] # list of (Factory_id, demand), LIFO
        self.status = 'IDLE'  # 'PICKING_UP', 'DELIVERING', 'LOADING', 'UNLOADING', 'WAITING', 'IDLE', 'OFFLINE'
        self.next_status_time = None  # time of next status change

    def __str__(self):
        return f"Vehicle({self.car_num})"

    def add_route(self, route):
        self.route = route

    def add_order(self, order, pickup_position, delivery_position):
        """
        Add an order to the vehicle, pick it up after pickup_position and deliver it after delivery_position
        :param delivery_position: pickup_position, pickup_position+1, pickup_position+2, ...
        :param pickup_position: 0, 1, 2, ...
        :param order:
        :return:
        """
        if pickup_position > delivery_position:
            raise ValueError("Pickup position should be less than delivery position")
        # 在self.assignment_list的索引为pickup_position的元素后插入(order.pickup_factory, order, 'PICK_UP')
        if not self.assignment_list:
            self.assignment_list.append((order.pickup_id, order, 'PICK_UP'))
            self.assignment_list.append((order.delivery_id, order, 'DELIVER'))
        else:
            self.assignment_list.insert(delivery_position + 1, (order.delivery_id, order, 'DELIVER'))
            self.assignment_list.insert(pickup_position + 1, (order.pickup_id, order, 'PICK_UP'))
        # self.assignment_list.insert(delivery_position + 1, (order.delivery_id, order, 'DELIVER'))
        # print(f"add_order at ({pickup_position}, {delivery_position}): {self.assignment_list}")
        self.history_info.append((self.now, 'add_order', order.pickup_id, 'condition 0', 'STILL'))

    def remove_order(self, order):
        """
        Remove an order from the vehicle
        :param order:
        :return:
        """
        for assignment in self.assignment_list:
            if assignment[1] == order:
                self.assignment_list.remove(assignment)
        # 不能移除正在进行的任务
        if self.current_assignment and self.current_assignment[1] == order:
            raise ValueError("Cannot remove the order that is currently being performed")

    def check_assignment_list(self, order, pickup_position, delivery_position) -> bool:
        """
        Check if the sequence of the assignment list is valid
        :return:
        """
        if pickup_position > delivery_position:
            return False
        cargo_list = [order.delivery_id for order in self.cargo]
        assignment_list = [assignment for assignment in self.assignment_list]
        if not assignment_list:
            return True
        # 货物匹配
        assignment_list.insert(delivery_position + 1, (order.delivery_id, order, 'DELIVER'))
        assignment_list.insert(pickup_position + 1, (order.pickup_id, order, 'PICK_UP'))
        if self.current_assignment[2] == 'PICK_UP':
            cargo_list.append(self.current_assignment[1].delivery_id)
        elif self.current_assignment[2] == 'DELIVER':
            # 卸货与货物
            if self.current_assignment[1].delivery_id != cargo_list.pop():
                return False
        for assignment in assignment_list:
            if assignment[2] == 'PICK_UP':
                cargo_list.append(assignment[1].delivery_id)
            else:
                if not cargo_list:
                    return False
                elif assignment[1].delivery_id != cargo_list.pop():
                    return False
        return True

    def check_capacity(self, order):
        """
        检查当前任务下的载重是否超过车辆容量
        :return:
        """
        load = 0
        for order in self.cargo:
            load += order.demand
        for assignment in self.assignment_list:
            # load
            if assignment[2] == 'PICK_UP':
                load += assignment[1].demand
            # unload
            else:
                load -= assignment[1].demand
            if load > self.capacity or load < 0:
                return False
            if load + order.demand > self.capacity:
                return False
        return True

    def print_information(self, test_print = 1):
        if test_print:
            print(f"=========={self.car_num}==========")
            print(f"history_info: {self.history_info}")
            print(f"current_assignment: {self.current_assignment}")
            print(f"assignment_list: {self.assignment_list}")
            print(f"cargo: {self.cargo}")
            print(f"status: {self.status}")
            print(f"next_status_time: {self.next_status_time}")
            print(f"now: {self.now}")
            print(f"delay: {self.delay}")
            print(f"distance: {self.distance}")
            print(f"----------{self.now}----------")

    def check_now(self) -> bool:
        """
        检查当前状态是否正确
        :return:
        """
        # 车辆空闲
        if self.status == 'IDLE':
            # 没有任何任务
            if self.current_assignment:
                return False
            elif self.assignment_list:
                return False
        # 正在送货
        elif self.status == 'DELIVERING':
            # 有货
            if not self.cargo:
                return False
            # 货物匹配
            if self.cargo[-1] != self.current_assignment[1]:
                return False
        return True
