#!/usr/bin/env python

import guessit
import argparse
import glob
import os
import shlex
import subprocess
import copy


def transcode(args):
    globs = (os.path.join(glob.escape(args.source), f"**/*.{x}") for x in args.formats)
    for g in globs:
        for file_path in glob.iglob(g, recursive=True):
            # save args for this file
            args = copy.deepcopy(args)

            # defalt output path
            out_path = file_path.removeprefix(args.source).removeprefix(os.path.sep)

            # better, guessed path
            if args.guessit:
                # entering: hell
                # population: you
                guessed = dict(guessit.guessit(file_path))
                ## are we dealing with an episode?
                if (
                    guessed.get("type", None) == "episode"
                    and sum([x in guessed for x in ["type", "title", "season", "episode"]]) == 4
                ):
                    # construct episode filename
                    out_path = guessed["title"]  # > Black Mirror
                    if "year" in guessed:
                        out_path += f' ({guessed["year"]})'  # > (2014)
                    prepend_path = out_path
                    out_path += f' S{guessed["season"]:02}E{guessed["episode"]:02}'  # > S03E04
                    if "episode_title" in guessed:
                        out_path += f' {guessed["episode_title"]}'  # > San Junipero
                    out_path += f".{args.output_format}"  # > .mkv

                    if args.no_long_path:  # i.e. if long path, store_false
                        out_path = os.path.join(prepend_path, f'Season {guessed["season"]}', out_path)
                        # > Black Mirror (2014)/Season 3/Black Mirror (2014) S03E04 San Junipero.mkv

            out_path = os.path.join(args.destination, out_path)
            # AND THAT WAS JUST THE OUTPUT FILE NAME
            # tired yet? i hope not, we haven't even invoked ffmpeg yet

            # invoke ffprobe
            probe_output = subprocess.check_output(("ffprobe", file_path), stderr=subprocess.STDOUT).decode()

            # codec fixing!
            ## fix libopus real quick (uwu)
            if args.audio_codec == "libopus" and "5.1(side)" in probe_output:
                args.audio_codec_args += ' -af "channelmap=channel_layout=5.1"'

            # prepare FFmpeg output environment
            os.makedirs(os.path.split(out_path)[0], exist_ok=True)

            ffmpeg_args = [
                "ffmpeg",
                "-i",
                file_path,
                "-map",
                "0",
            ]
            if args.video_codec:
                ffmpeg_args.extend(("-c:v", args.video_codec))
                if args.video_codec_args:
                    ffmpeg_args.extend(shlex.split(args.video_codec_args))
            if args.audio_codec:
                ffmpeg_args.extend(("-c:a", args.audio_codec))
                if args.audio_codec_args:
                    ffmpeg_args.extend(shlex.split(args.audio_codec_args))

            ffmpeg_args.append(out_path)
            subprocess.run(ffmpeg_args)

            if args.rm:
                os.remove(file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="directory to search for files")
    parser.add_argument("destination", help="directory to place finished transcodes")
    # file types
    parser.add_argument(
        "-f",
        "--formats",
        default=["mkv", "mp4"],
        help="the file extensions to look for",
        type=lambda x: x.split(","),
    )
    parser.add_argument("-F", "--output-format", default="mkv", help="the output container format")
    # codecs
    parser.add_argument(
        "-v", "--video-codec", default="libx265", help="the target video codec, set to empty string to ignore"
    )
    parser.add_argument(
        "-V",
        "--video-codec-args",
        default="",
        help="the arguments passed to the video codec",
    )
    parser.add_argument("-a", "--audio-codec", default="libopus", help="the target audio codec")
    parser.add_argument(
        "-A",
        "--audio-codec-args",
        default="",
        help="the arguments passed to the audio codec",
    )
    # output tuning
    parser.add_argument(
        "-g",
        "--guessit",
        action="store_true",
        help="attempt to guess and prettify TV show filenames",
    )
    parser.add_argument(
        "--no-long-path",
        action="store_false",
        help="if guessit is enabled, moves all files to the root of the output directory",
    )
    parser.add_argument("--rm", action="store_true", help="delete source file after successful transcode")

    args = parser.parse_args()
    transcode(args)
