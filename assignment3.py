# Placing imports below
import argparse
import csv
import re
import urllib.request
from collections import Counter
from datetime import datetime

# Regex
IMAGE_REGEX = re.compile(r".*\.(jpg|gif|png)$", re.IGNORECASE)
BROWSER_REGEXES = {
    "Firefox": re.compile(r"Firefox", re.IGNORECASE),
    "Safari": re.compile(r"Safari", re.IGNORECASE),
    "Chrome": re.compile(r"Chrome", re.IGNORECASE),
    "Internet Explorer": re.compile(r"MSIE|Trident", re.IGNORECASE),
}

def download_file(url):
    response = urllib.request.urlopen(url)
    return [line.decode("utf-8") for line in response.readlines()]

def process_log(log_lines):
    reader = csv.reader(log_lines)
    total_requests = 0
    image_requests = 0
    browser_counter = Counter()
    hour_counter = Counter()

    for row in reader:
        if len(row) < 3:
            continue

        path, dt_str, user_agent = row [0], row[1], row[2]

        # Counting the image hits
        if IMAGE_REGEX.match(path):
            image_requests += 1

        # Counting the browser
        for browser, pattern in BROWSER_REGEXES.items():
            if pattern.search(user_agent):
                browser_counter[browser] += 1
                break

        # Counting hour
        try:
            dt = datetime.strptime(dt_str, "%m %d %Y %H:%M:%S")
            hour_counter[dt.hour] += 1
        except ValueError:
            continue

        total_requests += 1

    return total_requests, image_requests, browser_counter, hour_counter

def main(url):
    parser = argparse.ArgumentParser()
    parser.add_argument("--url",
                        required=True,
                        help="http://s3.amazonaws.com/cuny-is211-spring2015/weblog.csv")
    args = parser.parse_args()

    log_lines = download_file(args.url)
    total, image_hits, browsers, hours = process_log(log_lines)

    # stats
    if total > 0:
        percent = (image_hits / total) * 100
        print(f"Image requests account for {percent:.1f}% of all requests")
    else:
        print(f"No image requests found.")

    # Finding out which browser is most popular
    if browsers:
        most_common_browser = browsers.most_common(1)[0][0]
        print(f"The most popular browser is: {most_common_browser}")
    else:
        print(f"No browser information found.")

    # Hits per hour
    print("\nHits per hour:")
    for hour, count in sorted(hours.items(), key=lambda x: x[1], reverse=True):
        print(f"Hour {hour:02d} has {count} hits.")

    print(f"Running main with URL = {url}...")


if __name__ == "__main__":
    """Main entry point"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--url",
                        help="http://s3.amazonaws.com/cuny-is211-spring2015/weblog.csv",
                        type=str,
                        required=True)
    args = parser.parse_args()
    main(args.url)

