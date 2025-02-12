import os
import yaml
import json
import tempfile
import unittest
from pathlib import Path


def convert_yaml_to_json(directory):
    """
    Convert all YAML files in the given directory to JSON format.

    Args:
        directory (str): Path to the directory containing YAML files
    """
    # Ensure the directory exists
    if not os.path.exists(directory):
        raise ValueError(f"Directory '{directory}' does not exist")

    # Get all .yaml files in the directory
    yaml_files = Path(directory).glob("*.yaml")

    for yaml_path in yaml_files:
        try:
            # Create corresponding JSON filename
            json_path = yaml_path.with_suffix(".json")

            # Read YAML file
            with open(yaml_path, "r") as yaml_file:
                yaml_content = yaml.safe_load(yaml_file)

            # Write JSON file
            with open(json_path, "w") as json_file:
                json.dump(yaml_content, json_file, indent=2)

            print(f"Converted {yaml_path} to {json_path}")

        except yaml.YAMLError as e:
            print(f"Error parsing {yaml_path}: {e}")
        except Exception as e:
            print(f"Error processing {yaml_path}: {e}")


class TestYAMLToJSONConverter(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up temporary directory and its contents
        for file in Path(self.test_dir).glob("*"):
            file.unlink()
        os.rmdir(self.test_dir)

    def test_basic_conversion(self):
        # Create a test YAML file
        yaml_content = """
        name: Test User
        age: 30
        hobbies:
          - reading
          - coding
        """
        yaml_path = Path(self.test_dir) / "test.yaml"
        with open(yaml_path, "w") as f:
            f.write(yaml_content)

        # Convert the file
        convert_yaml_to_json(self.test_dir)

        # Check if JSON file was created
        json_path = yaml_path.with_suffix(".json")
        self.assertTrue(json_path.exists())

        # Verify JSON content
        with open(json_path) as f:
            json_data = json.load(f)

        self.assertEqual(json_data["name"], "Test User")
        self.assertEqual(json_data["age"], 30)
        self.assertEqual(json_data["hobbies"], ["reading", "coding"])

    def test_invalid_yaml(self):
        # Create an invalid YAML file
        invalid_yaml = """
        invalid:
          - unclosed bracket: [
        """
        yaml_path = Path(self.test_dir) / "invalid.yaml"
        with open(yaml_path, "w") as f:
            f.write(invalid_yaml)

        # Conversion should not raise an exception
        convert_yaml_to_json(self.test_dir)

        # Check that no JSON file was created
        json_path = yaml_path.with_suffix(".json")
        self.assertFalse(json_path.exists())

    def test_empty_directory(self):
        # Directory exists but has no YAML files
        convert_yaml_to_json(self.test_dir)
        # Should not create any files
        self.assertEqual(len(list(Path(self.test_dir).glob("*.json"))), 0)

    def test_nonexistent_directory(self):
        # Test with a directory that doesn't exist
        with self.assertRaises(ValueError):
            convert_yaml_to_json("/nonexistent/directory")

    def test_complex_yaml(self):
        # Test with a more complex YAML structure
        yaml_content = """
        server:
          host: localhost
          port: 8080
          settings:
            timeout: 30
            retry: true
            nested:
              key1: value1
              key2: 
                - item1
                - item2
        environment: production
        """
        yaml_path = Path(self.test_dir) / "complex.yaml"
        with open(yaml_path, "w") as f:
            f.write(yaml_content)

        convert_yaml_to_json(self.test_dir)

        json_path = yaml_path.with_suffix(".json")
        with open(json_path) as f:
            json_data = json.load(f)

        self.assertEqual(json_data["server"]["host"], "localhost")
        self.assertEqual(json_data["server"]["port"], 8080)
        self.assertEqual(
            json_data["server"]["settings"]["nested"]["key2"], ["item1", "item2"]
        )
        self.assertEqual(json_data["environment"], "production")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        convert_yaml_to_json(sys.argv[1])
    else:
        unittest.main()
