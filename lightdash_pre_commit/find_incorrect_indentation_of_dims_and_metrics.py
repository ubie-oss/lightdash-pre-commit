import argparse
from typing import Optional, Sequence

import yaml


def find_indentation_issues(data: dict) -> list:
    errors = []

    for model in data.get("models", []):
        for column in model.get("columns", []):
            if "config" in column and "meta" in column["config"]:
                # Check additional_dimensions under dimension
                if "dimension" in column["config"]["meta"]:
                    if "additional_dimensions" in column["config"]["meta"]["dimension"]:
                        errors.append(
                            f"Incorrect indent: 'additional_dimensions' should not be a child of 'dimension' "
                            f"for column: {column.get('name')}."
                        )

                    # Check metrics under dimension
                    if "metrics" in column["config"]["meta"]["dimension"]:
                        errors.append(
                            f"Incorrect indent: 'metrics' should not be a child of 'dimension' for column:"
                            f" {column.get('name')}."
                        )

                # Check metrics under additional_dimensions
                if "additional_dimensions" in column["config"]["meta"]:
                    for ad_key, ad_value in column["config"]["meta"][
                        "additional_dimensions"
                    ].items():
                        if ad_key == "metrics":
                            errors.append(
                                f"Incorrect indent: 'metrics' should not be a child of "
                                f"'additional_dimensions' at key '{ad_key}' in column: {column.get('name')}."
                            )

    return errors


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames", nargs="*", help="Filenames to check for indentation correctness"
    )
    args = parser.parse_args(argv)

    error_flag = False
    for file_path in args.filenames:
        try:
            with open(file_path, "r") as file:
                data = yaml.safe_load(file)
                errors = find_indentation_issues(data)
                if errors:
                    print(f"Errors found in '{file_path}':")
                    for error in errors:
                        print(error)
                    error_flag = True
        except Exception as e:
            print(f"Failed to process '{file_path}': {e}")
            error_flag = True

    if error_flag:
        return 1

    return 0


if __name__ == "__main__":
    exit(main(None))
