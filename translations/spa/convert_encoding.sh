#!/bin/sh

vim "$@" '+set nomore' '+:argdo :edit ++enc=latin1 ++ff=dos | :write ++enc=utf-8 ++ff=unix' '+:q'
