import argparse
from typing import Optional, Sequence

import yaml


def find_duplicates(data: dict) -> list:
    all_names = {}  # Dictionary to track both metrics and dimensions
    errors = []

    # Check for metrics and dimensions defined at the model 'meta' level
    for model in data.get("models", []):
        # Process model-level metrics
        if (
            "config" in model
            and "meta" in model["config"]
            and "metrics" in model["config"]["meta"]
        ):
            for metric, details in model["config"]["meta"]["metrics"].items():
                all_names[metric] = all_names.get(metric, 0) + 1

        # Check for metrics and dimensions defined at the column level
        for column in model.get("columns", []):
            # Process column-level dimensions
            if (
                "config" in column
                and "meta" in column["config"]
                and "dimension" in column["config"]["meta"]
            ):
                column_name = column["name"]
                all_names[column_name] = all_names.get(column_name, 0) + 1

            # Process column-level additional dimensions
            if (
                "config" in column
                and "meta" in column["config"]
                and "additional_dimensions" in column["config"]["meta"]
            ):
                for ad_dim, ad_details in column["config"]["meta"][
                    "additional_dimensions"
                ].items():
                    all_names[ad_dim] = all_names.get(ad_dim, 0) + 1

            # Process column-level metrics
            if (
                "config" in column
                and "meta" in column["config"]
                and "metrics" in column["config"]["meta"]
            ):
                for metric_name, details in column["config"]["meta"]["metrics"].items():
                    all_names[metric_name] = all_names.get(metric_name, 0) + 1

    # Check for duplicates and gather error messages
    for name, count in all_names.items():
        if count > 1:
            errors.append(
                f"Duplicate name '{name}' used {count} times (as metrics or dimensions)."
            )

    return errors


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to check")
    args = parser.parse_args(argv)

    error_flag = False
    for file_path in args.filenames:
        try:
            with open(file_path, "r") as file:
                data = yaml.safe_load(file)
                errors = find_duplicates(data)
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
