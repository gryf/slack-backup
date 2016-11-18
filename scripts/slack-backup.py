#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create backup for certain date for specified channel in slack
"""
import argparse
import pprint

from slack_backup import client


def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument("token", help="Slack token - a string, which can be"
                        " generated/obtained via "
                        "https://api.slack.com/docs/oauth-test-tokens page")
    # parser.add_argument("channel", help="Slack channel name")
    args = parser.parse_args()

    slack = client.Client(args.token)

    pprint.pprint(slack.get_hisotry(selected_channels=['elysium']))


if __name__ == "__main__":
    main()
