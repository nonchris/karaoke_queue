from functools import cache
from typing import Union, Any

from rapidfuzz import process
from jarowinkler import jarowinkler_similarity

from karaoke_queue.data_models.song import Song
from karaoke_queue.database import songs_db
from karaoke_queue.database.db_getters import get_all_songs

# the song DB will probably not update during a session
# so we can cache the results
# TODO: make update function in case something changed anyways
__all_song_query: list[tuple] = get_all_songs(fields=("title", "artist"))

ALL_TITLES_LIST: tuple[str, ...] = tuple(song for song, artist in __all_song_query)
ALL_ARTISTS_LIST: tuple[str, ...] = tuple(artist for song, artist in __all_song_query)

# some things to make life easier, there types are not in the types.py module since they're only used internally
__levenshtein_result = list[tuple[str, Any, int]]
__levenshtein_merged_result = list[tuple[tuple[str, str], float, int]]
__sort_after_score = lambda o: o[2]


def _get_best_n_matches_with_secondary_elements(
        query: str,
        first_choices: tuple[str],
        secondary_elements: tuple,
        limit=10,
        rank_secondary_elements=True
) -> tuple[__levenshtein_result, Union[list[str], __levenshtein_result]]:
    """
    Match strings from one list against a string using levenshtein distance
    Extract the elements at the most rated indices from list one, match those also to levenshtein

    Note: both lists need to have the "same" order, so that secondary_elements[i] belongs to choices[i] contextually
    The second list must be at least of the size as the first one!
    Args:
        query: string to match for
        first_choices: list to search for the best matches
        secondary_elements: list to extract the secondary matches from
        limit: how many results shall be extracted from the primary list
        rank_secondary_elements: True: secondary elements will be ranked, False: returns just list of secondary_elements

    Returns:
        two ranked lists, first the primary list ordered by score, second ordered by according element from first list
        if rank_secondary_elements:
            the second list contains rankings for the secondary elements
        else:
            just the elements
    """

    # preserve signature and still use a fancy decorator
    @cache
    def __inner(
            _query: str,
            _first_choices: tuple[str],
            _secondary_elements: tuple,
            _limit=10,
            _rank_secondary_elements=True
    ) -> tuple[__levenshtein_result, Union[list[str], __levenshtein_result]]:

        # get best matches from first dataset
        # (element value of choice, normalized edit distance, index of element or key if mapping)
        # https://maxbachmann.github.io/RapidFuzz/Usage/process.html#extract
        best_matches = process.extract(_query, _first_choices, limit=_limit, scorer=jarowinkler_similarity)
        # extract elements at the indices of good matches from first list
        second_list_elements = [_secondary_elements[i] for _, _, i in best_matches]

        if not _rank_secondary_elements:
            return best_matches, second_list_elements

        # rank the secondary elements, but sort them in the way the primary list is built
        ranked_secondary_list = sorted(process.extract(_query, second_list_elements), key=__sort_after_score)

        return best_matches, ranked_secondary_list

    return __inner(query, first_choices, secondary_elements, limit, rank_secondary_elements)


def __merge_ranks(ranked_titles: __levenshtein_result,
                  ranked_artists: __levenshtein_result
                  ) -> __levenshtein_merged_result:
    """ build new merged results list by merging title and artist as well as adding up their scores"""

    return [
        (
            (ranked_titles[i][0], ranked_artists[i][0]),
            ranked_titles[i][1] + ranked_artists[i][1],  # TODO do we need to divide it by 2 or something to be fair?
            ranked_titles[i][2]
        ) for i in range(len(ranked_titles))
    ]


def __merge_rank_with_unranked(
        ranked: __levenshtein_result,
        unranked_list: list[str],
        ranked_titles=True
) -> __levenshtein_merged_result:
    """ build new merged results list by combining title and artist """
    return [
        (
            # ensure that (title, artist) is always the tuples order
            (ranked[i][0], unranked_list[i]) if ranked_titles else (unranked_list[i], ranked[i][0]),
            ranked[i][1],
            ranked[i][2]
        ) for i in range(len(ranked))
    ]


def __deduplicate_result(
        to_deduplicate: Union[__levenshtein_merged_result]
) -> Union[__levenshtein_merged_result]:
    """ Find duplicates among the (title, artist) combinations, use the one with the highest score """

    output_dict = {}

    for item in to_deduplicate:
        title_artist = item[0]
        value = item[1:]

        if title_artist in output_dict:
            if value[0] > output_dict[title_artist][0]:  # if the new float value is greater
                output_dict[title_artist] = value
        else:
            output_dict[title_artist] = value

    # Convert back to list of tuples
    output_list = [(key, *value) for key, value in output_dict.items()]

    return output_list


# TODO maybe refactor this and the one below into one
def get_best_songs_title_match(
        query: str,
        limit=10,
) -> __levenshtein_merged_result:
    """ search only for matches in the titles """

    titles, artists = _get_best_n_matches_with_secondary_elements(
        query,
        ALL_TITLES_LIST,
        ALL_ARTISTS_LIST,
        limit=limit,
        rank_secondary_elements=False
    )

    merged = __merge_rank_with_unranked(titles, artists)
    deduplicated = __deduplicate_result(merged)

    return deduplicated


def get_best_songs_artist_match(
        query: str,
        limit=10,
) -> __levenshtein_merged_result:
    """ search only for matches in the artists """
    artists, titles = _get_best_n_matches_with_secondary_elements(
        query,
        ALL_ARTISTS_LIST,
        ALL_TITLES_LIST,
        limit=limit,
        rank_secondary_elements=False
    )

    merged = __merge_rank_with_unranked(artists, titles, ranked_titles=False)
    deduplicated = __deduplicate_result(merged)

    return deduplicated


def get_best_matched_songs(
        query: str,
        limit=10,
) -> list[Song]:
    """
    Search for best matches for a given query,
    by searching for best matches in title and best artists matches,
    then calculating the other attributes score,
    combining first and second attributes score for full ranking,
    then fetching the best songs from the Database

    Args:
        query: the string to search for
        limit: how many songs shall be returned at max

    Returns:
        list of the most likely songs
    """

    titles_primary, artists_secondary = _get_best_n_matches_with_secondary_elements(
        query, ALL_TITLES_LIST, ALL_ARTISTS_LIST, limit=limit, rank_secondary_elements=True
    )

    artists_primary, titles_secondary = _get_best_n_matches_with_secondary_elements(
        query, ALL_ARTISTS_LIST, ALL_TITLES_LIST, limit=limit, rank_secondary_elements=True
    )

    # ((title, artist), total_rank, index_of_full_list)
    title_first_list = __merge_ranks(titles_primary, artists_secondary)

    artist_first_list = __merge_ranks(titles_secondary, artists_primary)

    # TODO observe what impact these two solo-query cases have on a larger database
    title_only_search = get_best_songs_title_match(query, limit)

    artist_only_search = get_best_songs_artist_match(query, limit)

    all_results = title_first_list + artist_first_list  + title_only_search + artist_only_search

    all_ranks_unique = __deduplicate_result(all_results)

    all_ranks_unique_sorted = sorted(
        all_ranks_unique,
        key=__sort_after_score,
        reverse=True
    )

    to_query = all_ranks_unique_sorted[:limit]
    best_songs = [songs_db.get_song_by_title_and_author(*title_author) for title_author, _, _ in to_query]

    return best_songs
