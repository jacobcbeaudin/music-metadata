#!/usr/bin/env python3
import argparse
import logging
import os
from enum import Enum

import discogs_client
from mutagen.flac import FLAC
from pick import pick


class Logger:
    FORMAT = "%(levelname)s - %(filename)s:%(lineno)d - %(message)s"

    @classmethod
    def get_logger(cls, log_level=logging.INFO) -> logging.Logger:
        # Create a logger object
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)

        # Create a stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(log_level)

        # Create a formatter and add it to the handlers
        formatter = logging.Formatter(fmt=cls.FORMAT)
        stream_handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(stream_handler)

        return logger


logger = Logger.get_logger(log_level=logging.INFO)


class UserInput(Enum):
    YES = "Yes"
    NO = "No"


class FlacFile:
    TITLE_KEY = "title"
    ARTIST_KEY = "artist"
    GENRE_KEY = "Genre"

    @classmethod
    def get_metadata(cls, file_path: os.path) -> dict:
        metadata = {}
        audio = FLAC(file_path)
        if cls.TITLE_KEY in audio:
            title = audio[cls.TITLE_KEY][0]
            metadata[cls.TITLE_KEY] = title
        else:
            raise Exception("Title not found in metadata.")

        if cls.ARTIST_KEY in audio:
            artist = audio[cls.ARTIST_KEY][0]
            metadata[cls.ARTIST_KEY] = artist
        else:
            raise Exception("Artist not found in metadata.")

        logger.info(f"file path: {song_file}")
        for k, v in metadata.items():
            logger.info(f"\t{k}: {v}")

        return metadata

    @classmethod
    def set_genre(cls, file_path: os.path, styles: list[str]) -> None:
        prompt = "".join(
            [
                f"Setting styles:\n\t - ",
                "\n\t - ".join(styles),
                f"\nAdding as metadata to {song_file}",
                "\n\nPlease review before confirming metadata changes."
                "\n\nOriginal metadata listed below for reference:️",
                "".join([f"\n\t{k}: {v}" for k, v in flac_metadata.items()]),
                "\n\nData from Discogs API",
                "".join([f"\n\t{k}: {v}" for k, v in discogs_metadata_content.items()]),
            ]
        )

        option, _ = pick(
            options=[e.value for e in UserInput],
            title=prompt,
            indicator="=>",
            default_index=0,
        )

        option = UserInput(option)

        if UserInput.YES == option:
            audio = FLAC(file_path)

            # TODO: ask Juan how to handle multiple Genres
            audio[cls.GENRE_KEY] = ";".join(styles)
            logger.info(f"Adding genres: {styles} to {file_path}")
            audio.save()
            logger.info(f"Added genres: {styles} to {file_path}")

        elif UserInput.NO == option:
            logger.info(f"No changes made for {song_file}")

        else:
            raise Exception("pick works unexpectedly")


class SongLookup:
    TITLE_KEY = "Title"
    ARTISTS_KEY = "Artists"
    YEAR_KEY = "Year"
    COUNTRY_KEY = "Country"
    LABELS_KEY = "Labels"
    FORMAT_KEY = "Format"
    STYLES_KEY = "Styles"
    GENRES_KEY = "Genres"

    def __init__(self, token: str):
        self.client = discogs_client.Client("MusicMetaData/0.1", user_token=token)

    @classmethod
    def parse_song_metadata_from_discogs(
        cls, release: discogs_client.models.Release
    ) -> dict:
        summary = dict()
        try:
            summary[cls.TITLE_KEY] = release.title
        except AttributeError:
            logger.error(f"'{cls.TITLE_KEY}' not found in Discogs API response")
        try:
            summary[cls.ARTISTS_KEY] = [artist.name for artist in release.artists]
        except AttributeError:
            logger.error(f"'{cls.ARTISTS_KEY}' not found in Discogs API response")
        try:
            summary[cls.YEAR_KEY] = release.year
        except AttributeError:
            logger.error(f"'{cls.YEAR_KEY}' not found in Discogs API response")
        try:
            summary[cls.COUNTRY_KEY] = release.country
        except AttributeError:
            logger.error(f"'{cls.COUNTRY_KEY}' not found in Discogs API response")
        try:
            summary[cls.LABELS_KEY] = [label.name for label in release.labels]
        except AttributeError:
            logger.error(f"'{cls.LABELS_KEY}' not found in Discogs API response")
        try:
            summary[cls.FORMAT_KEY] = [
                file_format["name"] for file_format in release.formats
            ]
        except AttributeError:
            logger.error(f"'{cls.FORMAT_KEY}' not found in Discogs API response")
        try:
            summary[cls.STYLES_KEY] = release.styles
        except AttributeError:
            logger.error(f"'{cls.STYLES_KEY}' not found in Discogs API response")
        try:
            summary[cls.GENRES_KEY] = release.genres
        except AttributeError:
            logger.error(f"'{cls.GENRES_KEY}' not found in Discogs API response")
        return summary

    def validate_song_with_database(
        self,
        title: str,
        artist: str,
    ) -> dict:
        release_candidates = self.client.search(
            title=title,
            # artist=artist,
        )

        if len(release_candidates) > 0:
            for release in release_candidates.page(0):
                release_summary = self.parse_song_metadata_from_discogs(release)
                diplay_info = "".join(
                    [
                        "Please verify if Metadata from discogs API is correct [Yes/No]:",
                        f"\n\tParsed from '{song_file}'",
                        f"\n\t\tTitle: {title}",
                        f"\n\t\tArtist: {artist}",
                        "\n\tRetrieved from discogs API:",
                        "".join(
                            [f"\n\t\t{k}: {v}" for k, v in release_summary.items()]
                        ),
                    ]
                )
                selected_input, _ = pick(
                    options=[e.value for e in UserInput],
                    title=diplay_info,
                    indicator="=>",
                    default_index=0,
                )

                selected_input = UserInput(selected_input)

                if UserInput.YES == selected_input:
                    return release_summary

        logger.error(
            f"Song could not be verified based on metadata in *.flac"
            f"\n\ttitle: {title}"
            f"\n\tartist: {artist}"
        )

        return {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="MusicMetadataEnrichment",
        description="adds genre / style metadata to *.flac files",
    )

    parser.add_argument(
        "-f",
        "--file-path",
        dest="file_path",
        help="file path to *.txt file containing file paths of selected *.flac file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    file_path = os.path.abspath(args.file_path)
    if not file_path.endswith(".txt"):
        *_, invalid_extension = file_path.split(".")
        invalid_extension = f".{invalid_extension}"
        raise Exception(
            f"Invalid text file extension: {invalid_extension}" "\nPlease use *.txt"
        )

    song_files = []
    with open(file_path) as song_list_file:
        for song_file in song_list_file.readlines():
            if song_file.endswith("\n"):
                song_file = song_file[: len(song_file) - 1]
            if not song_file.endswith(".flac"):
                *_, invalid_extension = file_path.split(".")
                invalid_extension = f".{invalid_extension}"
                raise Exception(
                    f"Invalid song file extension: {invalid_extension}"
                    "\nPlease use *.flac"
                )

            song_file = os.path.abspath(song_file)
            song_files.append(song_file)

    # Get token from https://www.discogs.com/settings/developers and set as environment variable
    token = os.environ.get("DISCOGSTOKEN")
    song_lookup = SongLookup(token=token)

    for song_file in song_files:
        flac_metadata = FlacFile.get_metadata(song_file)

        discogs_metadata_content = song_lookup.validate_song_with_database(
            title=flac_metadata.get(FlacFile.TITLE_KEY),
            artist=flac_metadata.get(FlacFile.ARTIST_KEY),
        )

        if SongLookup.STYLES_KEY in discogs_metadata_content:
            FlacFile.set_genre(
                file_path=song_file,
                styles=discogs_metadata_content.get(SongLookup.STYLES_KEY),
            )
