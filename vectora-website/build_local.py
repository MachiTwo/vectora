import subprocess
import sys


def main():
    print("Starting Hugo Build...")
    try:
        # Construct the command
        command = [
            "npx",
            "--yes",
            "hugo-bin",
            "--gc",
            "--minify",
        ]

        # Execute the command
        result = subprocess.run(command, check=True)

        if result.returncode == 0:
            print("\nBuild complete! Site generated in 'public/' directory.")
        else:
            print(f"\nBuild failed with return code: {result.returncode}")
            sys.exit(result.returncode)

    except subprocess.CalledProcessError as e:
        print(f"\nError during build: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
