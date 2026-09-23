import argparse
import json
from pathlib import Path

DB = Path("contacts.json")


def load():
    return json.loads(DB.read_text()) if DB.exists() else []


def cmd_list(args):
    for c in load():
        print(c["name"], c.get("phone", ""))


def main():
    parser = argparse.ArgumentParser(prog="contacts")
    sub = parser.add_subparsers(required=True)
    p_list = sub.add_parser("list")
    p_list.set_defaults(func=cmd_list)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
