from .data_models.session import Session


def get_session_admin_endpoint(session: Session, base="/v1/manage/{}/{}"):
    return base.format(session.name, session.uuid)


def get_session_user_endpoint(session: Session, base="/v1/user/{}"):
    return base.format(session.name)
