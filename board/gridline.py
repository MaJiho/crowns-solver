class Gridline:
    def __init__(self, position, thickness, orientation):
        """
        Initializes a Gridline object.

        Args:
            position (int): The position (index) of the gridline.
            thickness (int): The thickness of the gridline (in pixels).
            orientation (str): "horizontal" or "vertical" to indicate the orientation of the gridline.
        """
        self.position = position  # The position (center) of the gridline
        self.thickness = thickness  # The thickness of the gridline
        self.orientation = orientation  # "horizontal" or "vertical"
