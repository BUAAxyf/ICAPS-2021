class Order:
    """
    An order
    """
    def __init__(self, order_id, q_standard, q_small, q_box, demand,
                 creation_time, committed_completion_time, load_time, unload_time,
                 pickup_id, delivery_id):
        self.order_id = order_id
        # demand info
        self.q_standard = q_standard
        self.q_small = q_small
        self.q_box = q_box
        self.demand	= demand # total demand
        # time info
        self.creation_time	= creation_time
        self.committed_completion_time	= committed_completion_time
        self.load_time = load_time
        self.unload_time = unload_time
        # location info
        self.pickup_id = pickup_id
        self.delivery_id = delivery_id

    def __str__(self):
        return f"Order {self.order_id}"