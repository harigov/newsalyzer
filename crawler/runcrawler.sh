#!/bin/sh
CRAWLER_OUTPUT_DIR=~/Data
python crawler.py https://www.nytimes.com/section/world 10000 $CRAWLER_OUTPUT_DIR/nytimes/world
python crawler.py https://www.nytimes.com/section/us 10000 $CRAWLER_OUTPUT_DIR/nytimes/us
python crawler.py https://www.nytimes.com/section/politics 10000 $CRAWLER_OUTPUT_DIR/nytimes/politics
python crawler.py https://www.nytimes.com/pages/opinion 10000 $CRAWLER_OUTPUT_DIR/nytimes/opinion
python crawler.py http://www.nytimes.com/pages/business 10000 $CRAWLER_OUTPUT_DIR/nytimes/business
python crawler.py https://www.nytimes.com/section/technology 10000 $CRAWLER_OUTPUT_DIR/nytimes/technology
python crawler.py https://www.nytimes.com/section/science 10000 $CRAWLER_OUTPUT_DIR/nytimes/science
python crawler.py https://www.nytimes.com/section/health 10000 $CRAWLER_OUTPUT_DIR/nytimes/health