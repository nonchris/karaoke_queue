from karaoke_queue.data_models.exceptions import make_bad_request_exception


def try_convert_param_to_int(param: str, argument="") -> int:
    try:
        return int(param)

    except ValueError:
        msg = f"Can't convert to int: '{param}'"
        if argument:
            msg += f" for argument '{argument}'"

        raise make_bad_request_exception(msg)
