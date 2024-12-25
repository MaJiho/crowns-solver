import os
import unittest
from unittest.mock import patch, Mock

from screen_utils import capture_screenshot_of_grid


class TestCaptureScreenshotOfGrid(unittest.TestCase):
    @patch("pyautogui.screenshot")
    def test_valid_grid_area(self, mock_screenshot):
        # Mock the screenshot and save methods
        mock_image = Mock()
        mock_screenshot.return_value = mock_image
        mock_image.save = Mock()

        # Define a valid grid area and save path
        grid_area = (100, 100, 200, 200)
        save_path = "assets/test_grid_screenshot.png"

        # Call the function
        capture_screenshot_of_grid(grid_area, save_path)

        # Assert screenshot and save were called with correct arguments
        mock_screenshot.assert_called_once_with(region=(100, 100, 200, 200))
        mock_image.save.assert_called_once_with(save_path)

        # Cleanup test file if created
        if os.path.exists(save_path):
            os.remove(save_path)

    @patch("pyautogui.screenshot")
    def test_default_save_path(self, mock_screenshot):
        # Mock the screenshot and save methods
        mock_image = Mock()
        mock_screenshot.return_value = mock_image
        mock_image.save = Mock()

        # Define a valid grid area
        grid_area = (100, 100, 200, 200)

        # Call the function with default path
        capture_screenshot_of_grid(grid_area)

        # Assert screenshot and save were called with correct arguments
        mock_screenshot.assert_called_once_with(region=(100, 100, 200, 200))
        mock_image.save.assert_called_once_with("assets/grid_screenshot.png")

        # Cleanup test file if created
        if os.path.exists("assets/grid_screenshot.png"):
            os.remove("assets/grid_screenshot.png")

    @patch("pyautogui.screenshot")
    def test_invalid_grid_area(self, mock_screenshot):
        # Mock the screenshot method to raise a ValueError
        mock_screenshot.side_effect = ValueError("Invalid region dimensions")

        # Define an invalid grid area
        grid_area = (-100, -100, -200, -200)

        # Assert the function raises a ValueError
        with self.assertRaises(ValueError) as context:
            capture_screenshot_of_grid(grid_area)

        self.assertEqual(str(context.exception), "Invalid region dimensions")

    @patch("pyautogui.screenshot")
    def test_non_writable_save_path(self, mock_screenshot):
        # Mock the screenshot and save methods
        mock_image = Mock()
        mock_screenshot.return_value = mock_image
        mock_image.save = Mock(side_effect=PermissionError("Permission denied"))

        # Define a valid grid area and a non-writable path
        grid_area = (100, 100, 200, 200)
        save_path = "/non_writable_path/grid_screenshot.png"

        # Assert the function raises a PermissionError
        with self.assertRaises(PermissionError) as context:
            capture_screenshot_of_grid(grid_area, save_path)

        self.assertEqual(str(context.exception), "Permission denied")


if __name__ == '__main__':
    unittest.main()
