import sys
import os

# Fix import issues
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Processing.like import main as like_main


def run():
    print("Starting ATM Data Analysis...\n")

    like_main()

    print("\nAnalysis Completed Successfully!")


if __name__ == "__main__":
    run()