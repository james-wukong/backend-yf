from sqlmodel import Session, col, select

from app.models.relationships import Address, City, Country, State


def load_country(
    *, session: Session, country_in: dict[str, str | int]
) -> Country | None:
    statement = select(Country).where(
        col(Country.abbrev_2).ilike(country_in.get("country"))
    )
    return session.exec(statement).one_or_none()


def create_country(
    *,
    session: Session,
    country_in: dict[str, str | int],
) -> Country:
    country = load_country(session=session, country_in=country_in)
    if not country:
        country = Country.model_validate(
            country_in,
            update={
                "name": None,
                "abbrev_2": country_in.get("country"),
            },
        )
        try:
            session.add(country)
            session.commit()
            session.refresh(country)
        except Exception as e:
            session.rollback()
            print("Error creating country:", e)

    return country


def load_state(
    *,
    session: Session,
    state_in: dict[str, str | int],
    country: Country,
) -> State | None:
    statement = select(State).where(
        col(State.state_code).ilike(state_in.get("state")),
        State.country_id == country.id,
    )
    return session.exec(statement).one_or_none()


def create_state(
    *,
    session: Session,
    state_in: dict[str, str | int],
    country: Country,
) -> State:
    state = load_state(session=session, state_in=state_in, country=country)
    if not state:
        state_code = state_in.get("state") if state_in.get("state") else "UNKOWN"
        state = State.model_validate(
            state_in,
            update={
                "name": None,
                "state_code": state_code,
                "country_id": country.id,
            },
        )
        try:
            session.add(state)
            session.commit()
            session.refresh(state)

        except Exception as e:
            session.rollback()
            print("Error creating state:", e)

    return state


def load_city(
    *,
    session: Session,
    city_in: dict[str, str | int],
    state: State,
) -> City | None:
    statement = select(City).where(
        col(City.name).ilike(city_in.get("city")),
        City.state_id == state.id,
    )
    return session.exec(statement).one_or_none()


def create_city(
    *,
    session: Session,
    city_in: dict[str, str | int],
    state: State,
) -> City:
    city = load_city(session=session, city_in=city_in, state=state)
    if not city:
        city = City.model_validate(
            city_in,
            update={
                "name": city_in.get("city"),
                "state_id": state.id,
            },
        )
        try:
            session.add(city)
            session.commit()
            session.refresh(city)
        except Exception as e:
            session.rollback()
            print("Error creating city:", e)

    return city


def load_address(
    *,
    session: Session,
    address_in: dict[str, str | int],
    city: City,
) -> Address | None:
    statement = select(Address).where(
        col(Address.address).ilike(address_in.get("address")),
        col(Address.zip).ilike(address_in.get("zip")),
        Address.city_id == city.id,
    )
    return session.exec(statement).one_or_none()


def create_address(
    *,
    session: Session,
    address_in: dict[str, str | int],
    city: City,
) -> Address:
    address = load_address(session=session, address_in=address_in, city=city)
    if not address:
        address = Address.model_validate(
            address_in,
            update={
                "address": address_in.get("address"),
                "city_id": city.id,
            },
        )
        try:
            session.add(address)
            session.commit()
            session.refresh(address)
        except Exception as e:
            session.rollback()
            print("Error creating address:", e)

    return address
