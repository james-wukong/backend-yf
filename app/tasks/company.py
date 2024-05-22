from datetime import datetime
from sqlmodel import Session, select
from app.models.relationships import AddressProfile, Company
from app.services.address import (
    create_city,
    create_country,
    create_address,
    create_state,
)


async def create_company_profile(
    *,
    session: Session,
    profile_in: dict[str, str | int],
) -> None:
    country = create_country(
        session=session,
        country_in=profile_in,
    )
    state = create_state(
        session=session,
        state_in=profile_in,
        country=country,
    )
    city = create_city(
        session=session,
        city_in=profile_in,
        state=state,
    )
    address = create_address(
        session=session,
        address_in=profile_in,
        city=city,
    )
    try:
        ipodate: str = str(profile_in.get("ipoDate", ""))
        profile = Company.model_validate(
            profile_in,
            update={
                "company_name": profile_in.get("companyName"),
                "ipo_date": datetime.strptime(ipodate, "%Y-%m-%d").date(),
                "default_image": profile_in.get("defaultImage"),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "country_id": country.id,
            },
        )
        session.add(profile)
        session.commit()
        session.refresh(profile)
        statement = select(AddressProfile).where(
            AddressProfile.address_id == address.id,
            AddressProfile.profile_id == profile.id,
        )
        addr_profile = session.exec(statement).one_or_none()
        if not addr_profile:
            addr_profile = AddressProfile(
                is_main=False,
                address_id=address.id,
                profile_id=profile.id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            session.add(addr_profile)
            session.commit()
            session.refresh(addr_profile)
    except Exception as e:
        session.rollback()
        print("Error creating profile:", e)
