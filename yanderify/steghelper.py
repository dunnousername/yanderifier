# coding: utf-8
# This file contains code for an opt-out statistics program of sorts.
# If you don't like this, simply remove this file and this functionality will be disabled.
# If you have a bit more patience, here's an explanation.
#
# This file DOES NOT:
# - send any data to the network (you can check this for yourself by reading the code)
# - impact the quality of the output
# - modify any files besides the output files
# - reveal information about your system to anyone
# - tangibly affect performance of yanderify
# - visually watermark the output; this is downright unethical
# This file DOES:
# - add metadata to the encoded video (the year and episode id are modified)
#
# Deleting this file will not remove access to community resources, nor will it entitle you to them.
#
# Why?
# - We want to see how much use yanderify is getting so we can fully acknowledge the scale we are dealing with.
# - We want to set an example on polite ways to mark images for statistics (I'm looking at you, ifunny.co watermark)
# - As developers, we're interested to see how our program is getting used!
#
# Last updated: 1596509893 seconds since Jan 01, 1970 (UTC)

# This adds metadata to the video output. You probably won't notice these, and they don't show in embeds.
ffmpeg_flags = ' '.join([
# the year is 1686, after the i686 microarchitecture. it's just a nerd thing.
    '-metadata year="1686"',
# the "show" (whatever that means) is opus, the name of an open source audio codec.
# you've probably used it before without knowing it.
# the fact that an open standard can succeed in such wide adoption is amazing.
# again, just a nerd thing.
    '-metadata show="opus"',
# the episode number is 47. I've never actually played the game, but it seems quite good.
    '-metadata episode_id="47"'
])

# this concludes the file I wrote when I should have been writing actually useful code.